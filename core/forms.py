# Django
from django import forms

class BarcodeForm(forms.Form):
    barcode = forms.CharField(
        max_length=128,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escanear código de barras',
                'class': 'form-control',
                'aria-describedby': 'button-addon2',
                'autofocus': 'True',
                'autocomplete': 'off'
            }
        )
    )