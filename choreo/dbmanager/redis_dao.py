from django_redis import get_redis_connection
import pickle

"""
Activate this only for test, not running server
"""
# import os
#
# os.environ['DJANGO_SETTINGS_MODULE'] = 'choleor_choreo.settings'
# import django
#
# django.setup()


class UserRedisHandler:
    dao = get_redis_connection("user")

    # @staticmethod
    # def set_user_information(user_id, *info):
    #     _meta = ["audio_id", "start_idx", "end_idx", "counter", "interval_n"]
    #     for a,b in zip(_meta, info):
    #         UserRedisHandler.dao.hset(user_id, a, b)

    @staticmethod
    def set_user_counter(user_id, counter):
        """
        :param user_id counter
        :return: boolean flag
        """
        return UserRedisHandler.dao.hset(user_id, "counter", counter)

    @staticmethod
    def get_user_counter(user_id):
        """
        :param user_id:
        :return:
        """
        return int(UserRedisHandler.dao.hget(user_id, "counter").decode('UTF-8'))

    @staticmethod
    def get_user_info(user_id, *fields):
        res = []
        for i in range(len(fields)):
            res.append(UserRedisHandler.dao.hget(user_id, fields[i]).decode())
        print(res)
        return res

    @staticmethod
    def get_user_audio_slice_id(user_id):
        """
        :param user_id: string
        :return: list [audio_id, start_idx]
        """
        [audio_id, idx] = list(
            map(lambda x: x.decode('UTF-8'), UserRedisHandler.dao.hmget(user_id, "audio_id", "start_idx")))
        return audio_id + "ㅡ" + idx

    @staticmethod
    def get_user_audio_info(user_id):
        return UserRedisHandler.dao.hget(user_id, "partition").decode(
            'UTF-8') + ":" + UserRedisHandler.get_user_audio_slice_id(user_id)

    @staticmethod
    def set_process_result(user_id, choreos):
        for idx, val in enumerate(choreos):
            UserRedisHandler.dao.hset(user_id, str(idx + 1), str(val))


class SelectionRedisHandler:
    dao = get_redis_connection("selection")

    @staticmethod
    def add_selection_info(*args):
        """
        :param args: user_id (key), selected_choreo_id
        :return: boolean flag
        """
        SelectionRedisHandler.dao.rpush(*args)

    @staticmethod
    def get_selection_info(user_id):  # for test
        return [i.decode('UTF-8') for i in SelectionRedisHandler.dao.lrange(user_id, 0, -1)]


class AmplitudeRedisHandler:
    dao = get_redis_connection("amplitude")

    @staticmethod
    def set_amplitude_list(audio_slice_id, *args):
        AmplitudeRedisHandler.dao.rpush(audio_slice_id, *args)

    @staticmethod
    def get_amplitude_list(partition, audio_slice_id):
        """
        :param audio_slice_id: string, matched to user's choice step
        :return: amplitude list for the audio slice
        """
        # return list(reversed(
        #     [int(AmplitudeRedisHandler.dao.brpoplpush(audio_slice_id, audio_slice_id).decode('UTF-8')) for i in
        #      range(8)]))
        return pickle.loads(AmplitudeRedisHandler.dao.get(str(partition) + ":" + audio_slice_id))


class SimilarityRedisHandler:
    dao = get_redis_connection("similarity")

    @staticmethod
    def get_similarity_list(partition, audio_slice_id):
        """
        :param audio_slice_id: string
        :return: list of audio_slice_id in same cluster of given audio_slice_id(params)
        """
        """
        celery로 통신하지 않을 경우
        res = []
        for i in range(SimilarityRedisHandler.dao.llen(audio_slice_id)):
            res += [SimilarityRedisHandler.dao.brpoplpush(audio_slice_id, audio_slice_id).decode('UTF-8').split(":")]
        return list(reversed(res))
        """
        # celery 로 통신이 가능한 경우 --> key를 통해 바로 list 객체 받아옴 (decode는 아마 안해도 될듯)
        print(str(partition) + ":" + audio_slice_id)
        return pickle.loads(SimilarityRedisHandler.dao.get(str(partition) + ":" + audio_slice_id))
        # return list(reversed(list(map(lambda x: [x[0], float(x[1])],
        #                               [i.split(":") for i in
        #                                SimilarityRedisHandler.dao.get("celery-task-meta-" + audio_slice_id)]))))


if __name__ == '__main__':
    # UserRedisHandler.set_process_result("aa","c1","c2","c3","c4","c5","c6")
    # print(SimilarityRedisHandler.get_similarity_list("GNGbmg_pVlQㅡ9"))
    print(SelectionRedisHandler.get_selection_info("d495e100-5ba4-4e94-b1d0-df83fdc3f58e"))
