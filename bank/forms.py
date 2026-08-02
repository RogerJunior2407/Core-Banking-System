# bank/forms.py
from django import forms
from bank.models import Client

CURRENCY_CHOICES = [
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('GBP', 'GBP'),
    ('MAD', 'MAD'),
    ('FBI', 'FBI'),
]


class ClientLoginForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name / First Name'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class ClientSignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        required=True
    )
    currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        initial='USD',
        required=True,
        label='Preferred wallet currency',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Client
        fields = ['name', 'phone', 'age', 'adress']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name / First Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'adress': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
        }

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        return name

    def clean_currency(self):
        return (self.cleaned_data.get('currency') or '').upper()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class CreateWalletForm(forms.Form):
    currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        initial='USD',
        label='Currency',
        widget=forms.Select(attrs={'class': 'form-control'})
    )