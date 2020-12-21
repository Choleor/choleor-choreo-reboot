from django.urls import path
from . import views

urlpatterns = [
    path('video', views.video),
    path('thumbnail', views.thumbnail),
    path('check', views.check)
]
