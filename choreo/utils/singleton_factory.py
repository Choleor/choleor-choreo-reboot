class SingletonInstance:
    __instance = None

    @classmethod
    def __get_instance__(cls):
        __instance = cls.__instance

    @classmethod
    def instance(cls, *args, **kwargs):
        cls.__instance = cls(*args, **kwargs)
        cls.instance = cls.__get_instance__
        return cls.__instance
