from django import forms
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField
from .models import Donor
from django.forms import ModelForm

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal'),
)


class AddressForm(forms.Form):
    street_address = forms.CharField()
    apartment_address = forms.CharField()
    country = CountryField(blank_label="Select country").formfield(widget=CountrySelectWidget(attrs={
        "class":"custom-select d-block w-100"
    }))
    zip = forms.CharField(required=False)
    save_info = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)



class DonorCreateForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['name', 'blood_group', 'age', 'phone', 'address']