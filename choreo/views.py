from rest_framework.decorators import api_view
from choreo.processor.choreography_manager import *
import re
import os
import mimetypes
from wsgiref.util import FileWrapper
from django.http import FileResponse, StreamingHttpResponse
from choreo.external_handler.rabbitmq_handler import *
from configuration.config import *


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
def resp(request):
    """
    :param request: user_id, selected_choreo_id, counter
    :return: StreamingHttpResponse
    """
    _args = (request.data.get('user_id'), request.data.get('selected_choreo_id'), request.data.get('counter'))

    # rabbit mq 에 작업을 완료한 사항이 있는지 확인


    # 작업을 한 것이 없으면 아래의 코드 실행
    if not bool(request.data.get('remark')):  # remark가 0이면 Intro 혹은 Outro
        res = IntroManager(*_args).process() if _args[1] == "X" else BodyManager(*_args).process()
    else:  # remark가 1이면 마지막 안무를 선택해야 할 경우
        res = OutroManager(*_args).process()
    # Rabbitmq에 저장
    # response 보내고나서 celery로 directory 지우라고 시키기
    for i in res:
        return stream_video(request, i)
