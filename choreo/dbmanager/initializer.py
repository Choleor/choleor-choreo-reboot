import cv2
from choreo.utils.reader import CsvReader
import youtube_dlc
from choreo.models import *
from choreo.utils.utils import get_console_output
from choreo.dbmanager.redis_dao import *
import six, os
from time import sleep


class Initializer:
    csv1 = "/home/jihee/choleor_media/choreo/choreo_data.csv"
    csv2 = "/home/jihee/choleor_media/output.csv"
    csv_reader = CsvReader()

    data_n = None
    target_bpm = 100
    unique_cids = []
    choreo_csvinfo_dict = {}

    @staticmethod
    def choreo_csv_extractor(file="/home/jihee/choleor_media/csv/choreo_data.csv"):
        choreo = Initializer.csv_reader.read(file, **{'col1': 'choreo_id', 'col2': 'choreo_slice_id',
                                                      'col3': 'intro', 'col4': 'outro',
                                                      'col5': 'start_pose_type',
                                                      'col6': 'end_pose_type',
                                                      'col7': 'start_x_mean',
                                                      'col8': 'start_y_min', 'col9': 'start_y_max',
                                                      'col10': 'end_x_mean',
                                                      'col11': 'end_y_min', 'col12': 'end_y_max',
                                                      'col13': 'frame',
                                                      'col14': 'movement'})  # 리스트를 value로 갖는 dictionary
        keys = ['choreo_id', 'choreo_slice_id', 'intro', 'outro', 'start_pose_type', 'end_pose_type', 'start_x_mean',
                'start_y_min', 'start_y_max', 'end_x_mean', 'end_y_min', 'end_y_max', 'frame', 'movement']

        for k in keys:
            Initializer.choreo_csvinfo_dict[k] = []
            for i in range(len(choreo[k])):
                if bool(choreo['movement'][i]):
                    Initializer.choreo_csvinfo_dict[k] += [choreo[k][i]]

    @staticmethod
    def meta_csv_extractor(file="/home/jihee/choleor_media/csv/output.csv"):
        Initializer.choreo_csvinfo_dict['bpm'] = [0 if i is "" else float(i) for k, i in
                                                  enumerate(
                                                      Initializer.csv_reader.read(file, **{'col1': 'bpm'})['bpm'])]
        Initializer.choreo_csvinfo_dict['audio_id'] = Initializer.csv_reader.read(file, **{'col2': 'audio_id'})[
            'audio_id']
        Initializer.choreo_csvinfo_dict['choreo_vid'] = Initializer.csv_reader.read(file, **{'col3': 'choreo_vid'})[
            'choreo_vid']
        Initializer.choreo_csvinfo_dict['start_t'] = [int(i) for i in
                                                      Initializer.csv_reader.read(file, **{'col4': 'start'})['start']]

    @staticmethod
    def calculate_duration(path, audio_slice_id, extension):
        return get_console_output(
            'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {}/{}.{}'.format(
                path, audio_slice_id, extension))

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

    @staticmethod
    def __set_parameters__():
        Initializer.choreo_csv_extractor()
        Initializer.meta_csv_extractor()

        for i in Initializer.choreo_csvinfo_dict['choreo_id']:
            if i not in Initializer.choreo_csvinfo_dict['choreo_id']:
                Initializer.unique_cids += [i]
        """
        For downloading media - media initialize
        """
        Initializer.choreo_csvinfo_dict['url'] = ["http://www.youtube.com/watch?v=" + i for i in
                                                  Initializer.choreo_csvinfo_dict['choreo_id']]
        Initializer.choreo_csvinfo_dict['start_frs'] = []
        Initializer.choreo_csvinfo_dict['end_frs'] = []

        for i in Initializer.choreo_csvinfo_dict['frame']:
            Initializer.choreo_csvinfo_dict['start_frs'] += [int(i.split("~")[0]) + 10]
            Initializer.choreo_csvinfo_dict['end_frs'] += [int(i.split("~")[1]) - 10]

        for_join_cids = Initializer.choreo_csvinfo_dict['choreo_vid']
        for_join_bpms = Initializer.choreo_csvinfo_dict['bpm']
        for_join_aud_ids = Initializer.choreo_csvinfo_dict['audio_id']
        for_join_start_ts = Initializer.choreo_csvinfo_dict['start_t']

        bpms = []
        audios = []
        start_ts = []

        for i in Initializer.choreo_csvinfo_dict['choreo_id']:  # cid에 대해서
            if i in for_join_cids:  # output.csv (노래에도 있는 안무)
                bpm = for_join_bpms[for_join_cids.index(i)]
                bpms += [float(bpm)]
                audio = for_join_aud_ids[for_join_cids.index(i)]
                audios += [audio]
                start_t = for_join_start_ts[for_join_cids.index(i)]
                start_ts += [start_t]

        Initializer.choreo_csvinfo_dict['bpm'] = bpms
        Initializer.choreo_csvinfo_dict['audio_id'] = audios
        Initializer.choreo_csvinfo_dict['start_t'] = start_ts

        print(Initializer.choreo_csvinfo_dict['choreo_id'])
        print(Initializer.choreo_csvinfo_dict['audio_id'])
        print(Initializer.choreo_csvinfo_dict['bpm'])

        """
        For DB insertion
        """
        for i in range(len(Initializer.choreo_csvinfo_dict['choreo_id'])):
            Initializer.choreo_csvinfo_dict['intro'][i] = False if Initializer.choreo_csvinfo_dict['intro'][
                                                                       i] == "" else True
            Initializer.choreo_csvinfo_dict['outro'][i] = False if Initializer.choreo_csvinfo_dict['outro'][
                                                                       i] == "" else True

    @staticmethod
    def make_video(vid_links, cslice_ids, start, fps, start_frame, end_frame, bpm):
        """
        vidlink = [
            'https://www.youtube.com/watch?v=Zx1n1R_OQs0'
        ]
        fps = [0 for i in range(len(vidlink))]
        start_frame = [93+10] -> 93은 DB에서 가져온 start_frame, 해당 값에서 10 빼야함
        end_frame = [232-10] -> 232은 DB에서 가져온 end_frame, 해당 값에서 10 더해야함
        bpm = [72] -> 72은 DB에서 가져온 bpm

        download_video(vidlink, fps, start_frame, end_frame, bpm)
        """

        ydl = youtube_dlc.YoutubeDL({'format': '137', 'ignoreerrors': True}, )

        for idx in range(len(Initializer.choreo_csvinfo_dict['choreo_id'])):
            with ydl:
                video = ydl.extract_info(
                    vid_links[idx],
                    download=False
                )

            url = video['url']
            fps[idx] = video['fps']

            start_sec = ((start_frame[idx]) // fps[idx]) - 1
            end_sec = ((end_frame[idx]) // fps[idx]) + 1

            print(start_sec, end_sec, start[idx])

            start_time = Initializer.sec_to_time(start_sec + start[idx])
            duration_time = Initializer.sec_to_time(end_sec - start_sec + start[idx])

            try:
                os.system(
                    "ffmpeg -n -i '%s' -ss %s -t %s -async 1 -strict -2 '/home/jihee/choleor_media/choreo/TMP/vid1_%d.mp4'" % (
                        url, start_time, duration_time, idx))
            except:  # for error handling
                print(idx)
                pass

            vidcap = cv2.VideoCapture('/home/jihee/choleor_media/choreo/TMP/vid1_' + str(idx) + '.mp4')
            org_fps = vidcap.get(cv2.CAP_PROP_FPS)
            mod_fps = 60 * org_fps / bpm[idx]
            print(mod_fps)

            # 영상 길이 짧은 것들은 90bpm으로 변경
            # if(bpm[idx] <= 90):
            #    mod_fps = 60 * org_fps / bpm[idx]

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            if not os.path.exists(
                    "/home/jihee/choleor_media/choreo/SLICE/{}/".format(
                        Initializer.choreo_csvinfo_dict['choreo_id'][idx])):
                try:
                    os.mkdir("/home/jihee/choleor_media/choreo/SLICE/{}/".format(
                        Initializer.choreo_csvinfo_dict['choreo_id'][idx]))
                except:
                    pass
            print(Initializer.choreo_csvinfo_dict['choreo_id'][idx])
            out = cv2.VideoWriter(
                '/home/jihee/choleor_media/choreo/SLICE/{}/{}.mp4'.format(
                    Initializer.choreo_csvinfo_dict['choreo_id'][idx],
                    cslice_ids[idx]), fourcc, mod_fps,
                (1920, 1080))

            org_start_frame = (((start_frame[idx]) // fps[idx]) - 1) * fps[idx] + 1
            org_end_frame = (((end_frame[idx]) // fps[idx]) + 1) * fps[idx]

            count = 0

            while vidcap.isOpened():
                ret, image = vidcap.read()
                count += 1

                if count < start_frame[idx] - org_start_frame:
                    continue
                if count > end_frame[idx] - org_start_frame + 1:
                    break

                if ret is False:
                    break

                out.write(image)

            # os.remove('vid1_' + str(idx) + '.mp4')

            out.release()
            vidcap.release()

    @staticmethod
    def insert_db():
        print(len(Initializer.choreo_csvinfo_dict['choreo_id']))
        print(set(Initializer.choreo_csvinfo_dict['choreo_id']))

        for i in range(len(Initializer.choreo_csvinfo_dict['choreo_id'])):
            chor_id = Initializer.choreo_csvinfo_dict['choreo_id'][i]
            if chor_id == Initializer.choreo_csvinfo_dict['choreo_id'][i - 1]:
                continue
            Choreo(choreo_id=Initializer.choreo_csvinfo_dict['choreo_id'][i],
                   download_url="http://www.youtube.com/watch?v=" + Initializer.choreo_csvinfo_dict['choreo_id'][i],
                   bpm=Initializer.choreo_csvinfo_dict['bpm'][i]).save()

        for k in range(len(Initializer.choreo_csvinfo_dict['choreo_id'])):
            _duration = Initializer.calculate_duration("/home/jihee/choleor_media/choreo/SLICE/{}/".format(
                Initializer.choreo_csvinfo_dict['choreo_id'][k]), Initializer.choreo_csvinfo_dict['choreo_slice_id'][k],
                "mp4")
            try:
                real_dur = float(_duration)
                print(k, real_dur)
                ChoreoSlice(Initializer.choreo_csvinfo_dict['choreo_slice_id'][k],
                            Initializer.choreo_csvinfo_dict['movement'][k],
                            real_dur,
                            Initializer.choreo_csvinfo_dict['intro'][k],
                            Initializer.choreo_csvinfo_dict['outro'][k],
                            Initializer.choreo_csvinfo_dict['start_pose_type'][k],
                            Initializer.choreo_csvinfo_dict['end_pose_type'][k],
                            Initializer.choreo_csvinfo_dict['audio_id'][k] + "ㅡ" +
                            Initializer.choreo_csvinfo_dict['choreo_slice_id'][k].split("~")[1],
                            Initializer.choreo_csvinfo_dict['choreo_id'][k]).save()
            except Exception as e:
                print(e)
                pass

    @staticmethod
    def update_movement(*args):
        """
        :param args: choreo_silce_id1, [movement list1], ...
        :return:
        """
        if len(args) % 2 == 1:
            return ValueError

        for i in range(0, len(args), 2):
            ChoreoSlice.objects.filter(choreo_slice_id=args[i]).update(movement=":".join([str(x) for x in args[i + 1]]))

    @staticmethod
    def set_thumbnail():
        # 24fps로 변환
        for idx in range(len(Initializer.choreo_csvinfo_dict['choreo_id'])):
            print(Initializer.choreo_csvinfo_dict['choreo_id'][idx])
            print(Initializer.choreo_csvinfo_dict['choreo_slice_id'][idx])
            vidcap = cv2.VideoCapture(
                '/home/jihee/choleor_media/choreo/SLICE/{}/{}.mp4'.format(
                    Initializer.choreo_csvinfo_dict['choreo_id'][idx],
                    Initializer.choreo_csvinfo_dict[
                        'choreo_slice_id'][idx]))
            print(vidcap.isOpened())
            count = 0
            print(Initializer.choreo_csvinfo_dict['choreo_slice_id'][idx])
            while vidcap.isOpened():
                count += 1
                ret, image = vidcap.read()
                if ret is False:
                    break
                if count <= 10:
                    continue

                cv2.imwrite('/home/jihee/choleor_media/choreo/THUMBNAIL/{}.png'.format(
                    Initializer.choreo_csvinfo_dict['choreo_slice_id'][idx]), image)
                break

            vidcap.release()

    @staticmethod
    def initialize():
        Initializer.choreo_csv_extractor()
        Initializer.meta_csv_extractor()
        Initializer.__set_parameters__()
        # only execute when downloading video
        Initializer.make_video(Initializer.choreo_csvinfo_dict['url'],
                               Initializer.choreo_csvinfo_dict['choreo_slice_id'],
                               Initializer.choreo_csvinfo_dict['start_t'],
                               [0 for i in range(len(Initializer.choreo_csvinfo_dict['url']))],
                               Initializer.choreo_csvinfo_dict['start_frs'],
                               Initializer.choreo_csvinfo_dict['end_frs'],
                               Initializer.choreo_csvinfo_dict['bpm'])
        # Initializer.insert_db()
        # Initializer.set_thumbnail()


# if __name__ == '__main__':
# Initializer.initialize()
# Initializer.update_movement(
#     *(
#         "70dcSKN5Nx0~7", [10, 4, 9, 7, 5, 3, 2, 1, 1], "PDtdyNVYvgQ~10", [1, 4, 3, 5, 5, 3, 8, 9, 9],
#         "PDtdyNVYvgQ~11",
#         [3, 4, 2, 3, 2, 2, 4, 5, 9], "fVw8Eu8vG4M~10", [4, 5, 6, 7, 8, 8, 10, 3]))
# print(ChoreoSlice.objects.get(choreo_slice_id="k8ha7zI2P0Uㅡ10").movement)



    # for i in range(100):
    #     if UserRedisHandler.dao.hget("jihee", "4") is not None:
    #         try:
    #             UserRedisHandler.dao.hget("jihee", "4").decode()
    #             break
    #         except:
    #             print("I'll sleep")
    #             sleep(1)
    #             continue
    # print(res)

    # print("0" == UserRedisHandler.dao.hget("jihee", "2").decode())

if __name__ == '__main__':
    Initializer.initialize()