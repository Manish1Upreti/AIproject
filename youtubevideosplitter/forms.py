from django import forms

class YouTubeForm(forms.Form):
    url = forms.URLField(label='YouTube URL')
    clip_length = forms.IntegerField(label='Clip Length (seconds)', min_value=1)
