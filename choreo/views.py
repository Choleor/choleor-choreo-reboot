from rest_framework.decorators import api_view
# from choreo.processor.main_manager import *
from choreo.services.choreography_manager import *
import re
import os
from time import sleep
import mimetypes
import time, datetime
from wsgiref.util import FileWrapper
from django.http import FileResponse, StreamingHttpResponse, HttpResponse, JsonResponse
from choreo.processor.factory import Factory
from choreo.external_handler.rabbitmq_handler import *
from configuration.config import *


# from choreo.processor.choreography_manager import *


class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


def stream_video(request, choreography_file):
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    size = os.path.getsize(choreography_file)
    content_type, encoding = mimetypes.guess_type(choreography_file)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(RangeFileWrapper(open(choreography_file, 'rb'), offset=first_byte, length=length),
                                     status=206,
                                     content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(choreography_file, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp


@api_view(['POST'])
def video(request):
    """
    :param request: user_id, selected_choreo_id, counter(1-), remark, request_n(1-6)
    :return: StreamingHttpResponse
    """
    start = time.time()
    tmp_dic = request.data
    _args = (user_id, selected_choreo_id, counter, remark, request_n) = tmp_dic.get('user_id'), tmp_dic.get(
        'selected_choreo_id'), int(tmp_dic.get('counter')), int(tmp_dic.get('remark')), tmp_dic.get('request_n')
    print("REQUEST ARGUMENTS START")
    print(_args)
    print("REQUEST ARGUMENTS END")
    my_val = None

    if request_n == 1:
        _args = (user_id, selected_choreo_id, counter)
        if remark == 0:
            print("=============SELECT ON BODY===========")
            strategy = BodyStrategy(*_args)
        elif selected_choreo_id == "X":
            print("=============SELECT ON INTRO===========")
            strategy = IntroStrategy(*_args)
        else:
            print("=============SELECT ON BODY===========")
            strategy = OutroStrategy(*_args)

        my_val = ChoreographyManager(strategy).run_stgy()[0]
        for i in range(3):
            print("[NOTIFY FROM ROOT] I'm root process, this is the result")

    else:
        for i in range(100):
            try:
                resp = UserRedisHandler.dao.hget(user_id, str(request_n))
                if resp.decode() != '0':
                    my_val = UserRedisHandler.dao.hget(user_id, str(request_n)).decode()
                    print(f"[NOTIFY FROM {request_n}] I'm other process, this is my result")
                    print(my_val)
                    break
                else:
                    sleep(1)
            except Exception as e:
                sleep(2)
                continue

    print("[THIS IS MY VALUE] here's my value : " + my_val)

    partition = UserRedisHandler.dao.hget(user_id, "partition").decode()
    audio_id, start_idx, counter = [x.decode() for x in
                                    UserRedisHandler.dao.hmget(user_id, "audio_id", "start_idx", "counter")]
    audio_slice_id = audio_id + "ㅡ" + str(int(start_idx) + int(counter) - 1)
    # return HttpResponse(status=200)
    print("start to produce...")
    ret = Factory.produce(user_id, counter, partition, audio_slice_id, request_n, my_val)
    print("partition" + partition + "audio slice id" + audio_slice_id, ret)
    UserRedisHandler.dao.hset(user_id, str(request_n), '0')

    print("hello, this is your execution time")
    sec = time.time() - start
    times = str(datetime.timedelta(seconds=sec)).split(".")[0]
    print(times)
    return set_file_response(f"/home/jihee/choleor_media/product/{user_id}/{counter}/Mㅡ{my_val}.mp4", my_val)


@api_view(['POST'])
def thumbnail(request):
    start = time.time()
    tmp = request.data
    sel = None

    counter = tmp['counter']
    request_n = tmp['request_n']

    for i in range(100):
        try:
            t = UserRedisHandler.dao.hget(tmp['user_id'], str(tmp['request_n']))
            if t.decode() != '0':
                sel = t.decode()
                break
            else:
                sleep(1)
        except Exception:
            sleep(1)
            continue

    print("hello, this is your execution time")
    sec = time.time() - start
    times = str(datetime.timedelta(seconds=sec)).split(".")[0]
    print(times)
    print("before sending response")
    print(f"/home/jihee/choleor_media/choreo/THUMBNAIL/{sel}.png")
    return set_thumbnail_response(f"/home/jihee/choleor_media/choreo/THUMBNAIL/{sel}.png",
                                  f"{sel}")


def set_file_response(path, selected_choreo_id):
    response = HttpResponse(open(path, "rb"))
    response["Access-Control-Allow-Origin"] = "*"
    response['Content-Type'] = "application/octet-stream"
    response["choreo_id"] = selected_choreo_id
    response['Content-Disposition'] = f'attachment; filename="final.mp4"'  # wav만 보내지 않아도 되도록
    return response


def set_thumbnail_response(img_path, img_name):
    response = HttpResponse(open(img_path, "rb"))
    response["Access-Control-Allow-Origin"] = "*"
    response['Content-Type'] = "application/octet-stream"
    response['Content-Disposition'] = f'attachment; filename="{img_name}.png"'  # wav만 보내지 않아도 되도록
    return response


@api_view(['POST'])
def check(request):
    return HttpResponse(status=200, content="choreo-server")

