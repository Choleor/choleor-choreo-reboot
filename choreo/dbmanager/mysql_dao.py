from choreo.models import *
import django
from choreo.utils.singleton_factory import *

django.setup()


class ChoreoSliceHandler(SingletonInstance):
    @staticmethod
    def get_end_pose_type(_choreo_slice_id):
        return ChoreoSlice.objects.get(choreo_slice_id=_choreo_slice_id).end_pose_type

    @staticmethod
    def get_spose_cslice_aslice_list(_filter=None):
        """
        :param _filter: "Intro" / "Outro" / None
        :return: [[spose1, cslice1, aslice1],
                [spose2, cslice2, aslice2],
                ...] -> 2 dimension list
        """
        if _filter is None:  # body
            return ChoreoSlice.objects.values_list('start_pose_type', 'choreo_slice_id', 'audio_slice_id')
        else:
            return ChoreoSlice.objects.filter(intro=True).values_list('start_pose_type', 'choreo_slice_id',
                                                                      'audio_slice_id') \
                if filter == "Intro" else ChoreoSlice.objects.filter(outro=True).values_list('start_pose_type',
                                                                                             'choreo_slice_id',
                                                                                             'audio_slice_id')

    @staticmethod
    def get_movement_list(_choreo_slice_id):
        return ChoreoSlice.objects.values_list('movement')

    @staticmethod
    def get_movement_score(_choreo_slice_id):
        return ChoreoSlice.objects.get(choreo_slice_id=_choreo_slice_id)
