from django.core.cache import caches


class UserRedisHandler:
    dao = caches["user"]

    @staticmethod
    def set_user_counter(*args):
        """
        :param args: user_id(key), counter from client
        :return: boolean flag
        """
        UserRedisHandler.dao.hget(args[0], "counter", args[1])

    @staticmethod
    def get_user_audio(user_id):
        """
        :param user_id: string
        :return: list [audio_id, start_idx]
        """
        return [i.decode('UTF-8') for i in UserRedisHandler.dao.hmget(user_id, "audio_id", "start_idx")]


class SelectionRedisHandler:
    dao = caches["selection"]

    @staticmethod
    def add_selection_info(*args):
        """
        :param args: user_id (key), selected_choreo_id
        :return: boolean flag
        """
        SelectionRedisHandler.dao.rpush(args[0], [args[1]])


class AmplitudeRedisHandler:
    dao = caches["amplitude"]

    @staticmethod
    def get_amplitude_list(audio_slice_id):
        """
        :param audio_slice_id: string, matched to user's choice step
        :return: amplitude list for the audio slice
        """
        return reversed([AmplitudeRedisHandler.dao.brpoplpush(audio_slice_id, audio_slice_id).decode('UTF-8') for i in range(8)])


class SimilarityRedisHandler:
    dao = caches["similarity"]

    @staticmethod
    def get_similarity_list(audio_slice_id):
        """
        :param audio_slice_id: string,
        :return: list of audio_slice_id in same cluster of given audio_slice_id(params)
        """
        return [SimilarityRedisHandler.dao.brpoplpush(audio_slice_id, audio_slice_id).decode('UTF-8').split(":") for i in
                range(SimilarityRedisHandler.dao.llen(audio_slice_id))]
