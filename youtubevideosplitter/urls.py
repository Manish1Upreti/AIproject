# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.index, name='index')
# ]

#for restfulapi
from django.urls import path
from .views import YouTubeDownloadSplitAPI

urlpatterns = [
    path('api/download-split/', YouTubeDownloadSplitAPI.as_view(), name='download_split_api'),
]
