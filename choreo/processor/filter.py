from abc import ABC
from choreo.dbmanager.mysql_dao import ChoreoSliceHandler


class Filter(ABC):
    @staticmethod
    def filter(*args):
        """
        :param args: filter option -- Intro / Outro / Body
        :return:
        """
        pass


class PhaseFilter(Filter):
    """
    Intro / Body /Outro 구간에 기반한 filter
    """

    @staticmethod
    def filter(*args):
        """
        :param args: selected_choreo_id, state
        :return:
        """
        return [list(i) for i in ChoreoSliceHandler.get_spose_cslice_aslice_list(_filter=args[1])]


class ConnectivityFilter(PhaseFilter):
    @staticmethod
    def filter(*args):
        filter_res = PhaseFilter.filter(args)
        prev_end_pose_type = ChoreoSliceHandler.get_end_pose_type(args[0])
        for i in filter_res:
            if ConnectivityFilter.__similarity_degree__(int(prev_end_pose_type, 2), int(i[0])) == -1:
                del i
        return filter_res

    @staticmethod
    def __similarity_degree__(first, second):
        """
        :param first:
        :param second:
        :return:
        """
        ret = 0
        idx = [18, 16]  # 몸의 방향
        for i in range(2):
            temp1 = (first >> idx[i]) & int('11', 2)
            temp2 = (second >> idx[i]) & int('11', 2)

            if temp1 != temp2:
                return -1

        idx = [12, 8, 4, 0]
        for i in range(4):
            temp1 = (first >> idx[i]) & int('1111', 2)
            temp2 = (second >> idx[i]) & int('1111', 2)
            result = bin(temp1 ^ temp2)[2:].count('1')

            if result > 1:
                return -1
            else:
                ret += result

        if ret > 2:
            return -1

        return ret  # 0(높은 포즈 우선순위) 1, 2, -1 (부적합)
