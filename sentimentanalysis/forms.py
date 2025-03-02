from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
    chart_type = forms.ChoiceField(choices=[('bar', 'Bar Chart'), ('pie', 'Pie Chart')])
    palette = forms.ChoiceField(choices=[('viridis', 'Viridis'), ('pastel', 'Pastel'), ('Set2', 'Set2'), ('coolwarm', 'Coolwarm'), ('Blues', 'Blues')])
