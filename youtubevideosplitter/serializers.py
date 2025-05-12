# serializers.py
from rest_framework import serializers

class YouTubeDownloadSerializer(serializers.Serializer):
    url = serializers.URLField()
    clip_length = serializers.IntegerField(min_value=1)
