from abc import ABC
from choreo.dbmanager.redis_dao import SelectionRedisHandler
from abc import ABC, abstractmethod
from choreo.dbmanager.mysql_dao import ChoreoSliceHandler


class Filter(ABC):
    def __init__(self, _filter):
        self._filter = _filter

    @abstractmethod
    def filter(self, *args):
        pass


class PhaseFilter(Filter):
    """
    Intro / Body /Outro 구간에 기반한 filter
    """

    def __init__(self, _filter):
        self._filter = _filter

    def filter(self, *args):
        print("PHASE FILTER")
        print(self._filter)
        filter_res = [list(i) for i in ChoreoSliceHandler.get_spose_cslice_aslice_list(_filter=self._filter)]
        if len(filter_res) >= 6:
            print(filter_res)
            return args[0], filter_res
        else:
            return args[0], [list(i) for i in ChoreoSliceHandler.get_spose_cslice_aslice_list(_filter=None)]


class ConnectivityFilter(PhaseFilter):
    """
    Only for body, outro filter
    """

    def __init__(self, _filter):
        self._filter = _filter

    def filter(self, *args):
        """
        :param args: user_id, selected_choreo_id
        :return:
        """
        print(self._filter)

        in_filter_res = PhaseFilter(self._filter).filter(args[0])[1]

        print("==================phase filter=================")
        print(in_filter_res)

        print("==================end pose type of previous choreography================")
        prev_end_pose_type = ChoreoSliceHandler.get_end_pose_type(args[1])
        print(prev_end_pose_type)

        ret_filter_res = []
        for v in in_filter_res:
            # exclude previous choreo
            if v[1].split("~")[0] == args[1].split("~")[0]:
                in_filter_res.remove(v)

        for v in in_filter_res:
            pose_match_score = ConnectivityFilter.__similarity_degree__(prev_end_pose_type, v[0])
            v += [pose_match_score]
            if pose_match_score != -1:
                ret_filter_res.append(v)

        print("==================before going to selector==================")
        if len(ret_filter_res) >= 6:
            print("==================[FILTER] more than 6==================")
            print(args[0])
            print(ret_filter_res)
            return args[0], ret_filter_res
        else:
            print("==================[FILTER] less than 6==================")
            print(args[0], in_filter_res)
            ret_for_sub_res = []

            for i in ret_filter_res:
                ret_for_sub_res.append(i)

            for k in in_filter_res:
                if k not in ret_filter_res:
                    ret_for_sub_res += [k]

            print(ret_for_sub_res)
            return args[0], ret_for_sub_res

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


# if __name__ == '__main__':
# PhaseFilter Test
# print(PhaseFilter.filter("", "intro"))  # intro
# intro_res = [[87189, "-xmVz8BiLRo~0", "HE5wgGCxGHcㅡ0"],
#        [135441, "4X6TsiWZtJo~0", "lN47Figg8gQㅡ0"],
#        [20885, "70dcSKN5Nx0~0", "QM8HngracYYㅡ0"],
#        [34905, "CM5VSP1QWXg~0", "tz0OzH6fHrIㅡ0"],
#        [273, "dVPexyKjj_k~0", "M3ctXZBingMㅡ0"],
#        [4373, "fVw8Eu8vG4M~0", "Pp8sHP - s87Iㅡ0"],
#        [17, "GwCiHS9_3 - Y~0", "Pu1tIIdLYKEㅡ0"],
#        [533, "HJX8X1il7Ow~0", "Cf6_oDpe6rEㅡ0"],
#        [4369, "k98iZjftvKQ~0", "2i4zg9PzXYMㅡ0"],
#        [273, "P3EgWidZthc~0", "EZk1HsQvi5Qㅡ0"],
#        [17, "PDtdyNVYvgQ~0", "k8ha7zI2P0Uㅡ0"],
#        [8465, "QwXHFKWmCgw~0", "xqMYU4_kEqkㅡ0"],
#        [17, "S8fvgFDQKvk~0", "a4AeHG4l5fQㅡ0"],
#        [41617, "yNM2DU3fkgE~0", "EKiJMxGBZi8ㅡ0"],
#        [39317, "Zx1n1R_OQs0~0", "RQTgJRwMdKQㅡ0"]]

# print(len(PhaseFilter.filter("", None)))  # body

# print(PhaseFilter.filter("", "outro"))  # outro
# outro_res = [[795136, '-xmVz8BiLRo~7', 'HE5wgGCxGHcㅡ7'], [6549, '70dcSKN5Nx0~14', 'QM8HngracYYㅡ14'],
#              [4369, 'CM5VSP1QWXg~6', 'tz0OzH6fHrIㅡ6'], [33041, 'dVPexyKjj_k~14', 'M3ctXZBingMㅡ14'],
#              [27153, 'fVw8Eu8vG4M~14', 'Pp8sHP-s87Iㅡ14'], [8725, 'GwCiHS9_3-Y~12', 'Pu1tIIdLYKEㅡ12'],
#              [137617, 'jSrxXduIz1U~10', 'GNGbmg_pVlQㅡ10'], [811392, 'k98iZjftvKQ~17', '2i4zg9PzXYMㅡ17'],
#              [4113, 'NPmHcrvc8-w~9', '0NUb7guya5wㅡ9'], [8725, 'P3EgWidZthc~8', 'EZk1HsQvi5Qㅡ8'],
#              [8721, 'PDtdyNVYvgQ~12', 'k8ha7zI2P0Uㅡ12'], [807189, 'QDqlB8M25DQ~15', 'VMaIEj-zyNwㅡ15'],
#              [8721, 'QwXHFKWmCgw~13', 'xqMYU4_kEqkㅡ13'], [38233, 'RHTqzSSl5qU~19', 'DycottXjONkㅡ19'],
#              [34833, 'S8fvgFDQKvk~11', 'a4AeHG4l5fQㅡ11'], [4369, 'v4CILLmw6EE~26', 'XlpTLDulFe8ㅡ26'],
#              [4369, 'yNM2DU3fkgE~7', 'EKiJMxGBZi8ㅡ7'], [37269, 'Zx1n1R_OQs0~19', 'RQTgJRwMdKQㅡ19']]

# Connectivity Filter Test
# notice that this filter is not applied to intro
# print("Body")
# print(ConnectivityFilter().filter("70dcSKN5Nx0~6", None)) # body
# print("Outro")
# if __name__ == '__main__':
    # o, v = ConnectivityFilter(_filter="outro").filter("I'm user", "QDqlB8M25DQ~8")  # outro
