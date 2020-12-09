class ExtractChoreography:
    def __init__(self, song):
        self.__song = song
        self.__song_score = []
        self.__choreo_score = []
        self._harmony_unnormalized = []
        self._harmony_normalized = []
        self._similarity_unnormalized = []  # 나중에 get_music_similarity_score에서 가져오는 값으로 초기화
        self._similarity_normalized = []
        self._final_score = []

    def get_audio_similarity_score(self, a):
        # TODO redis에서 빼오기
        # self._similarity_scores_unnormalized = Process().get_similarity_score()
        return a

    def get_audio_score(self, audio_score):
        # TODO song score 객체 has-a로 갖든.. setting 로직
        self.__song_score = audio_score

    def set_choreo_score(self, choreo_score):
        self.__choreo_score = choreo_score

    def extract_harmony_score(self):
        """
        :param song_score: [[],[],[],..]
        :param choreo_score: [[],[],[],..]
        :return:
        """
        if not len(self.__song_score) == len(self.__choreo_score):
            raise Exception("Length of two score lists are different.")

        for k, l in zip(self.__song_score, self.__choreo_score):
            if len(k) != len(l):
                raise Exception("Length of two score lists are different")

        self._harmony_unnormalized = [(sum([abs(i - j) for i, j in zip(k, l)]) / len(k)) for k, l in
                                      zip(self.__song_score, self.__choreo_score)]
        return self._harmony_unnormalized

    def normalize_scores(self):
        property_list = [[self._similarity_unnormalized, self._similarity_normalized],
                         [self._harmony_unnormalized, self._harmony_normalized]]
        for score in property_list:
            score[1] = list(map(lambda x: ((x - min(score[0])) / (max(score[0]) - min(score[0]))) * 50 + 50, score[0]))
        self._similarity_normalized, self._harmony_normalized = property_list[0][1], property_list[1][1]
        return self._similarity_normalized, self._harmony_normalized

    def avg_scores(self):
        self._final_score = [(i + j) / 2 for i, j in zip(self._similarity_normalized, self._harmony_normalized)]
        return self._final_score

    def extract_final_score(self):
        # TODO 다 초기값으로 바꾸기, reduce로 함수형 프로그래밍 형태로 리팩토링
        self.get_audio_similarity_score([3, 5, 1])
        self.get_audio_score([[3, 5, 6, 8], [4, 10, 1, 5, 10], [3, 1, 5]])
        self.set_choreo_score([[5, 9, 1, 10], [10, 2, 5, 8, 2], [4, 10, 3]])
        self.extract_harmony_score()
        self.normalize_scores()
        self.avg_scores()
        return self._final_score


if __name__ == '__main__':
    # expected_res = [3.25, 5.8, 4.0]
    eob = ExtractChoreography([])
    eob.get_audio_score([3, 5, 1])
    res = eob.extract_harmony_score([[3, 5, 6, 8], [4, 10, 1, 5, 10], [3, 1, 5]],
                                    [[5, 9, 1, 10], [10, 2, 5, 8, 2], [4, 10, 3]])
    # eob.normalize_scores()
    # eob.avg_scores()
    eob.extract_final_score()
