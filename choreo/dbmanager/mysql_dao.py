from choreo.models import *


class ChoreoSliceHandler:
    @staticmethod
    def get_end_pose_type(_choreo_slice_id):
        return int(ChoreoSlice.objects.get(choreo_slice_id=_choreo_slice_id).end_pose_type)

    @staticmethod
    def get_spose_cslice_aslice_list(_filter=None):
        """
        :param _filter: "Intro" / "Outro" / None
        :return: [[spose1, cslice1, aslice1],
                [spose2, cslice2, aslice2],
                ...] -> 2 dimension list
        """
        if _filter is None:  # body
            return list(
                ChoreoSlice.objects.all().exclude(intro=True).exclude(outro=True).order_by(
                    'choreo_slice_id').values_list(
                    'start_pose_type', 'choreo_slice_id',
                    'audio_slice_id'))
        else:
            print("current filter is " + _filter)
            if _filter == "intro":
                return list(
                    ChoreoSlice.objects.filter(intro=True).order_by('choreo_slice_id').values_list('start_pose_type',
                                                                                                   'choreo_slice_id',
                                                                                                   'audio_slice_id'))
            else:
                return list(
                    ChoreoSlice.objects.filter(outro=True).order_by('choreo_slice_id').values_list('start_pose_type',
                                                                                                   'choreo_slice_id',
                                                                                                   'audio_slice_id'))

    @staticmethod
    def get_movement_list():
        return [int(i) for i in ChoreoSlice.objects.values_list('movement', flat=True)[0].split(",")]

    @staticmethod
    def get_movement_score(_choreo_slice_id):
        return [int(i) for i in ChoreoSlice.objects.get(choreo_slice_id=_choreo_slice_id).movement.split(",")]

    @staticmethod
    def insert_all(*args):
        Choreo.save(
            Choreo(choreo_id=args[8], download_url="http://www.youtube.com/v?" + args[8], start_sec=0.00,
                   end_sec=0.00))
        ChoreoSlice.save(
            ChoreoSlice(choreo_slice_id=args[0], movement=args[1], duration=args[2], intro=args[3], outro=args[4],
                        start_pose_type=args[5], end_pose_type=args[6], audio_slice_id=args[7], choreo_id_id=args[8]))

    @staticmethod
    def flush_all():
        ChoreoSlice.objects.all().delete()
        Choreo.objects.all().delete()


if __name__ == '__main__':
    # ChoreoSliceHandler.insert_all("ymZGEY0OAzkㅡ4", "3,4,6,7,9", 3.28, False, False, b"010101001010010",
    #                               b"10000100000010", "EZk1HsQvi5Q", "ymZGEY0OAzk")
    # print(ChoreoSliceHandler.get_movement_score("ymZGEY0OAzkㅡ4"))
    # print(ChoreoSliceHandler.get_movement_list())
    # print(ChoreoSliceHandler.get_end_pose_type("ymZGEY0OAzkㅡ4"))
    # print(ChoreoSliceHandler.get_spose_cslice_aslice_list(_filter=None))  # 처음거는 나중에 필요하면 decode

    ChoreoSliceHandler.flush_all()
    ChoreoSliceHandler.insert_all(*(("akskdkvnksl_31", "3,4,6,7,9", 3.28, False, True, b"010101001010010",
                                     b"10000100000010", "APVLDKEKQA", "akskdkvnksl")))
    print(ChoreoSlice.objects.all().values_list('start_pose_type', 'choreo_slice_id', 'audio_slice_id'))
    ChoreoSliceHandler.insert_all(*(("ymZGEY0OAzkㅡ4", "2,4,6,7,1", 4.28, False, False, b"010101001010010",
                                     b"10111100000010", "EZk1HsQvi5Qㅡ15", "ymZGEY0OAzk")))
    print(ChoreoSlice.objects.all().values_list('start_pose_type', 'choreo_slice_id', 'audio_slice_id'))
    ChoreoSliceHandler.insert_all(*("zdosfdkekㅡ1", "1,10,9,9,4", 5.24, True, False, b"010101001010010",
                                    b"10000100000010", "EZk1HsQvi5Qㅡ14", "zdosfdkek"))
    print(ChoreoSlice.objects.all().values_list('start_pose_type', 'choreo_slice_id', 'audio_slice_id'))
    ChoreoSliceHandler.insert_all(*(("ymZGEY0OAzkㅡ4", "3,4,6,7,9", 3.28, False, False, b"010101001010010",
                                     b"10000100000010", "EZk1HsQvi5Q", "ymZGEY0OAzk")))
    print(ChoreoSlice.objects.all().values_list('start_pose_type', 'choreo_slice_id', 'audio_slice_id'))
    ChoreoSliceHandler.insert_all(*(("ymZGEY0OAzkㅡ5", "2,4,6,7,1", 4.28, False, False, b"010101001010010",
                                     b"10111100000010", "EZk1HsQvi5Qㅡ16", "ymZGEY0OAzk")))
    print(list(ChoreoSlice.objects.all().values_list('start_pose_type', 'choreo_slice_id', 'audio_slice_id')))
    ChoreoSliceHandler.insert_all(*("ymZGEY0OAzkㅡ26", "1,10,9,9,4", 5.24, False, True, b"010101001010010",
                                    b"10000100000010", "EZk1HsQvi5Qㅡ26", "ymZGEY0OAzk"))
    print(list(ChoreoSlice.objects.all().values_list('start_pose_type', 'choreo_slice_id', 'audio_slice_id')))
