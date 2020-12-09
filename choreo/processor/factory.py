from abc import *
from configuration.config import *
from choreo.utils.utils import get_console_output


class Factory(metaclass=ABCMeta):
    @staticmethod
    def produce(user_id, counter, audio_slice_id, *args):  # 다 동일하다면 이거 하나를 받는게 낫지 않을까?
        audio_duration = get_console_output(
            'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {}.wav'.format(
                audio_slice_id))

        product_path_lists = []

        for choreo_slice_id in args:  # multiprocessing
            choreo_duration = get_console_output(
                'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {}.mp4'.format(
                    choreo_slice_id))
            # speedup
            get_console_output(
                'ffmpeg -i {}.mp4 -vf  "setpts={}*PTS" {}'.format(
                    F_SLICE + choreo_slice_id.split("ㅡ") + choreo_slice_id,
                    choreo_duration / audio_duration,
                    choreo_slice_id))  # speedup
            # merge
            product_path = "{}/USER/{}_{}/{}.mp4".format(MEDIA_PATH, user_id, counter, choreo_slice_id)
            get_console_output(
                'ffmpeg -i "choreo/SLICE/{}/{}.mp4" -i "audio/SLICE/{}/{}.wav" "{}"'.format(
                    choreo_slice_id.split("ㅡ"), choreo_slice_id,
                    audio_slice_id.split("ㅡ"), audio_slice_id, product_path))
            product_path_lists += product_path

        return product_path_lists
