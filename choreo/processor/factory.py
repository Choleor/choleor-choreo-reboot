from abc import ABC
from configuration.config import *
from choreo.utils.utils import get_console_output
import os
import cv2
from choreo.utils.reader import CsvReader

import warnings

warnings.filterwarnings('ignore')

"""
#함수 호출 예시

slice_id = ['Zx1n1R_OQs0ㅡ1']
target_bpm = 105 -> 사용자가 input한 음악의 bpm --> 평균 비피엠!

editor = CrossEditor()
editor.change_video_to_target_bpm(slice_id, target_bpm)
"""


class Factory:
    frame_dct = {}
    bpm_dct = {}

    @staticmethod
    def produce(user_id, counter, partition, audio_slice_id, request_n, choreo_slice_id):
        print(user_id, counter, partition, audio_slice_id, request_n, choreo_slice_id)
        print(choreo_slice_id)
        audio_path = AUDIO_SLICE_PATH + str(partition) + "/" + audio_slice_id.split("ㅡ")[0]
        audio_duration = float(
            Factory.calculate_duration(audio_path, audio_slice_id, "wav"))
        audio_bpm = 60 / (audio_duration / 8)
        start_frs, end_frs = [], []
        products = []
        Factory.get_frame_info()
        print(audio_bpm)

        # for choreo_slice_id in choreos:
        # print(choreo_slice_id)

        sf, ef = Factory.frame_dct.get(choreo_slice_id)[0], Factory.frame_dct.get(choreo_slice_id)[1]
        start_frs += [sf]
        end_frs += [ef]
        print(sf, ef)

        if not os.path.exists(f"/home/jihee/choleor_media/product/{user_id}/"):
            try:
                os.mkdir(f"/home/jihee/choleor_media/product/{user_id}/")
            except:
                pass

        if not os.path.exists(f"/home/jihee/choleor_media/product/{user_id}/{counter}"):
            try:
                os.mkdir(f"/home/jihee/choleor_media/product/{user_id}/{counter}")
            except:
                pass

        Factory.change_video_to_target_bpm(
            path=f'/home/jihee/choleor_media/product/{user_id}/{counter}/'.format(user_id=user_id,
                                                                                  counter=counter),
            cslice_id=choreo_slice_id, counter=counter, target_bpm=audio_bpm, request_n=request_n)

        # for choreo_slice_id in choreos:
        product_1 = f"/home/jihee/choleor_media/product/{user_id}/{counter}/{choreo_slice_id}.mp4"
        product_2 = f"/home/jihee/choleor_media/product/{user_id}/{counter}/Mㅡ{choreo_slice_id}.mp4"

        Factory.combine_music("{}/{}.wav".format(audio_path, audio_slice_id), product_1, product_2)
        products += [product_2]
        print(products[0])
        return products

    @staticmethod
    def get_frame_info(_file="/home/jihee/choleor_media/csv/choreo_data.csv"):
        """
        :param file:
        :return:
        """
        # csv에서 읽어오기
        csv_info = CsvReader().read(_file, **{'col1': 'frame', 'col2': 'choreo_slice_id'})
        for idx, val in enumerate(csv_info['choreo_slice_id']):
            Factory.frame_dct[val] = list(map(lambda x: int(x), csv_info['frame'][idx].split("~")))
        return Factory.frame_dct

    @staticmethod
    def calculate_duration(path, audio_slice_id, extension):
        return get_console_output(
            'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {}/{}.{}'.format(
                path, audio_slice_id, extension))

    @staticmethod
    def change_video_to_target_bpm(path, counter, cslice_id, target_bpm, request_n):
        vidlink = f"{path}/{cslice_id}.mp4"

        # 영상 앞 뒤로 10 frame 삭제
        vidcap = cv2.VideoCapture(f'/home/jihee/choleor_media/choreo/SLICE/{cslice_id.split("~")[0]}/{cslice_id}.mp4')

        fps = vidcap.get(cv2.CAP_PROP_FPS);
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f"{path}/vvid{counter}_{request_n}.mp4", fourcc, fps, (1920, 1080))

        count = 0
        max_count = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)

        while vidcap.isOpened():
            count += 1
            ret, image = vidcap.read()
            if ret is False:
                break
            if count <= 10 or count >= max_count - 10:
                continue
            out.write(image)

        vidcap.release()
        out.release()

        # 24fps로 변환
        os.system(
            f"ffmpeg -i '{path}/vvid{counter}_{request_n}.mp4' -r 24 -y '{path}/vid{counter}_{request_n}.mp4'")
        # os.remove(f"{path}/vvid{idx}_{request_n}.mp4")

        # 영상 속도 target bpm맞게 변환
        target_fps = target_bpm * 24 / 120
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(vidlink, fourcc, target_fps, (1920, 1080))

        vidcap = cv2.VideoCapture(f'{path}/vid{counter}_{request_n}.mp4')

        while vidcap.isOpened():
            ret, image = vidcap.read()
            if ret is False:
                break
            out.write(image)

        # os.remove(f"{path}/vid{idx}_{request_n}.mp4")
        vidcap.release()
        out.release()

    @staticmethod
    def combine_music(aud, vid, product):
        return get_console_output(
            'ffmpeg -i "{}" -i "{}" "{}"'.format(aud, vid, product))

    # ffmpeg에 시간 정보 넣어주기 위해 사용
    @staticmethod
    def sec_to_time(sec):
        time = ""
        temp = 0
        for i in range(3):
            temp = sec % 60
            time = str(sec % 60) + time if temp >= 10 else "0" + str(temp) + time
            sec //= 60
            if i < 2:
                time = ":" + time
        return time


if __name__ == '__main__':
    # ser_id, counter, partition, audio_slice_id, request_n, *choreos
    Factory.produce("dk-39823n9", 1, 5, "A0vq3jLAoQgㅡ14", 1, 'u1CYPY61uPI~6')
# print(Factory.get_frame_info()["S8fvgFDQKvk~0"])
