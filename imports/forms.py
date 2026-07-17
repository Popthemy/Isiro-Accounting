"""Forms for the imports app."""

from django import forms


class UploadForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={"class": "form-input", "accept": ".pdf,.csv"}))
    bank_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. Bank of Africa (optional)"}))
