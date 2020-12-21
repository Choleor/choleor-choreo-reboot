from django.db import models
from django.core.cache import cache
from configuration.config import *

"""
Activate configuration code below only when not running server
"""
# import os
# import django
#
# os.environ['DJANGO_SETTINGS_MODULE'] = 'choleor_choreo.settings'
# django.setup()


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        pass

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        # self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()

    @classmethod
    def load(cls):
        if cache.get(cls.__class__.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
            print(obj.__str__())
            return cache.get(cls.__class__.__name__)


class Choreo(SingletonModel):
    choreo_id = models.CharField(primary_key=True, max_length=50)
    download_url = models.URLField(max_length=150)
    bpm = models.FloatField(default=0.00)

    def __str__(self):
        return self.choreo_id


class ChoreoSlice(SingletonModel):
    choreo_slice_id = models.CharField(primary_key=True, max_length=50)
    movement = models.CharField(default="-", max_length=130)
    duration = models.FloatField(default=0.00)
    intro = models.BooleanField(default=False)
    outro = models.BooleanField(default=False)
    start_pose_type = models.IntegerField(default=-1)
    end_pose_type = models.IntegerField(default=--1)
    audio_slice_id = models.CharField(max_length=40)
    choreo_id = models.ForeignKey(Choreo, on_delete=models.CASCADE)

    def __str__(self):
        return self.choreo_slice_id
