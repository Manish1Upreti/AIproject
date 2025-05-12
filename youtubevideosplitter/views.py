# import os
# import traceback
# from django.conf import settings
# from django.shortcuts import render
# from .forms import YouTubeForm
# from moviepy.video.io.VideoFileClip import VideoFileClip
# from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
# import yt_dlp
#
# def download_video(url, output_dir):
#     ydl_opts = {
#         'format': 'best',
#         'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
#     }
#
#     downloaded_path = None
#
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=True)
#             filename = ydl.prepare_filename(info)
#             downloaded_path = filename
#             print(f"Download successful: {downloaded_path}")
#     except Exception as e:
#         print(f"Error downloading video: {e}")
#         raise Exception(f"Error downloading video: {e}")
#
#     return downloaded_path
#
# def split_video(video_path, clip_length, output_dir):
#     clips = []
#
#     try:
#         if not video_path or not os.path.isfile(video_path):
#             raise Exception(f"Video file not found: {video_path}")
#
#         print(f"Loading video: {video_path}")
#         video = VideoFileClip(video_path)
#         duration = int(video.duration)
#         video.close()
#
#         print(f"Video duration: {duration} seconds")
#         base_name = os.path.splitext(os.path.basename(video_path))[0]
#
#         for start in range(0, duration, clip_length):
#             end = min(start + clip_length, duration)
#             clip_filename = f"{base_name}_clip_{start}_{end}.mp4"
#             clip_path = os.path.join(output_dir, clip_filename)
#
#             print(f"Creating clip: {clip_path} ({start}s to {end}s)")
#             ffmpeg_extract_subclip(video_path, start, end, clip_path)
#             clips.append(clip_path)
#
#         return clips
#
#     except Exception as e:
#         traceback.print_exc()
#         raise Exception(f"Error splitting video file '{video_path}': {e}")
#
# def index(request):
#     clips = []
#     error = None
#
#     if request.method == 'POST':
#         form = YouTubeForm(request.POST)
#         if form.is_valid():
#             url = form.cleaned_data['url']
#             length = form.cleaned_data['clip_length']
#
#             if "youtube.com/watch" not in url and "youtu.be" not in url:
#                 error = "Invalid YouTube URL. Please enter a valid video link."
#             else:
#                 try:
#                     download_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
#                     os.makedirs(download_dir, exist_ok=True)
#
#                     video_path = download_video(url, download_dir)
#                     clips = split_video(video_path, length, download_dir)
#                     clips = [os.path.relpath(clip, settings.MEDIA_ROOT) for clip in clips]
#                 except Exception as e:
#                     error = str(e)
#     else:
#         form = YouTubeForm()
#
#     return render(request, 'index.html', {
#         'form': form,
#         'clips': clips,
#         'error': error,
#         'MEDIA_URL': settings.MEDIA_URL
#     })
#
import os
import traceback
from django.conf import settings
from django.shortcuts import render
from .forms import YouTubeForm
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import yt_dlp

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .serializers import YouTubeDownloadSerializer


# --- Utility: Download Video ---
def download_video(url, output_dir):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
    }

    downloaded_path = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            downloaded_path = filename
            print(f"Download successful: {downloaded_path}")
    except Exception as e:
        print(f"Error downloading video: {e}")
        raise Exception(f"Error downloading video: {e}")

    return downloaded_path


# --- Utility: Split Video ---
def split_video(video_path, clip_length, output_dir):
    clips = []

    try:
        if not video_path or not os.path.isfile(video_path):
            raise Exception(f"Video file not found: {video_path}")

        print(f"Loading video: {video_path}")
        video = VideoFileClip(video_path)
        duration = int(video.duration)
        video.close()

        print(f"Video duration: {duration} seconds")
        base_name = os.path.splitext(os.path.basename(video_path))[0]

        for start in range(0, duration, clip_length):
            end = min(start + clip_length, duration)
            clip_filename = f"{base_name}_clip_{start}_{end}.mp4"
            clip_path = os.path.join(output_dir, clip_filename)

            print(f"Creating clip: {clip_path} ({start}s to {end}s)")
            ffmpeg_extract_subclip(video_path, start, end, clip_path)
            clips.append(clip_path)

        return clips

    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error splitting video file '{video_path}': {e}")


# --- Web Form View ---
def index(request):
    clips = []
    error = None

    if request.method == 'POST':
        form = YouTubeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            length = form.cleaned_data['clip_length']

            if "youtube.com/watch" not in url and "youtu.be" not in url:
                error = "Invalid YouTube URL. Please enter a valid video link."
            else:
                try:
                    download_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
                    os.makedirs(download_dir, exist_ok=True)

                    video_path = download_video(url, download_dir)
                    clips = split_video(video_path, length, download_dir)
                    clips = [os.path.relpath(clip, settings.MEDIA_ROOT) for clip in clips]
                except Exception as e:
                    error = str(e)
    else:
        form = YouTubeForm()

    return render(request, 'index.html', {
        'form': form,
        'clips': clips,
        'error': error,
        'MEDIA_URL': settings.MEDIA_URL
    })


# --- REST API View ---
class YouTubeDownloadSplitAPI(APIView):
    def post(self, request):
        serializer = YouTubeDownloadSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data['url']
            clip_length = serializer.validated_data['clip_length']

            if "youtube.com/watch" not in url and "youtu.be" not in url:
                return Response({"error": "Invalid YouTube URL"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                download_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
                os.makedirs(download_dir, exist_ok=True)

                video_path = download_video(url, download_dir)
                clips = split_video(video_path, clip_length, download_dir)
                clips_relative = [os.path.relpath(clip, settings.MEDIA_ROOT) for clip in clips]
                clip_urls = [settings.MEDIA_URL + path for path in clips_relative]

                return Response({"clips": clip_urls}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
