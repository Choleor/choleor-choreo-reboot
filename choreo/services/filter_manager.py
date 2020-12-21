from choreo.dbmanager.mysql_dao import ChoreoSliceHandler


class FilterManager:
    S_POSE = 0
    CHOREO = 1
    AUDIO = 2
    POSE_MATCH_SCORE = 3

    def __init__(self):
        self.phase_filtered = []
        self.pose_filtered = []
        self.selected_choreo_id = None
        self.phase = None

    def filter_with_phase(self, *args):
        """
        :param args: [0] selected_choreo_id  [1] stage
        :return:
        """
        self.selected_choreo_id = args[0]  # set selected choreo_id
        self.phase = args[1]

        no_duplicate_filtered = []

        filter_res = [list(i) for i in ChoreoSliceHandler.get_spose_cslice_aslice_list(_filter=self.phase)]

        if len(filter_res) >= 6:
            self.phase_filtered = filter_res
            print("I'm longer than 6 with PHASE FILTER")

        else:
            self.phase_filtered = [list(i) for i in ChoreoSliceHandler.get_spose_cslice_aslice_list(_filter=None)]
            print("I'm less than 6 with PHASE FLITER - INTRO/OUTRO > BODY")
        print("FILTERING FIN!!!!")
        print(self.phase_filtered[:6])
        # remove choreography in same videos with previous choreography
        for v in self.phase_filtered:
            if v[FilterManager.CHOREO].split("~")[0] != self.selected_choreo_id.split("~")[0]:
                no_duplicate_filtered.append(v)
            else:
                print("excluded because of my previous video..:(  " + v[FilterManager.CHOREO])

        print()
        print(len(no_duplicate_filtered))

        if len(no_duplicate_filtered) >= 6:
            print("finally no duplicate of previous stage!")
            self.phase_filtered = no_duplicate_filtered

        return self.phase_filtered

    def filter_with_pose(self):
        prev_end_pose_type = ChoreoSliceHandler.get_end_pose_type(self.selected_choreo_id)
        sub = []
        self.pose_filtered = []
        for v in self.phase_filtered:
            pose_match_score = FilterManager.__similarity_degree__(prev_end_pose_type, v[FilterManager.S_POSE])
            v.append(pose_match_score)
            sub += [v]
            if pose_match_score != -1:
                self.pose_filtered.append(v)

        print(str(len(sub)) + "  vs  " + str(len(self.pose_filtered)))

        if len(self.pose_filtered) < 6:
            print("No meaning of pose")
            self.pose_filtered = sub
        else:
            print("MEANINGFUL POSE FILTER")

        return self.pose_filtered

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


class PhaseFilter(FilterManager):
    def filter(self, *args):
        return self.filter_with_phase(*args)


class PoseFilter(FilterManager):
    def filter(self, *args):
        self.filter_with_phase(*args)
        return self.filter_with_pose()
