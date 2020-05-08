from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('stripe',"Stripe"),
    ('paypal',"Pay Pal"),
)

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'Promo Code',
        'arial-label':"Recipient's username",
        "aria-describedby":"basic-addon2"
    }))

class CheckoutForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'id':'firstName','class':'form-control'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'id':'lastName','class':'form-control'
    }))
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'id':'email','class':'form-control'
    }))
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'id':'address','class':'form-control'
    }))
    zipcode = forms.CharField(widget=forms.TextInput(attrs={
        'id':'zip','class':'custom-select d-block w-100'
    }))
    mobile_no = forms.IntegerField(widget=forms.TextInput(attrs={
        'id':'mob_no','class':'form-control'
    }))
    apartment_address = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'id':'address-2','class':'form-control'
    }))
    country = CountryField(blank_label='(Select Country)').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100','id':'country'
    }))
    same_billing_address = forms.BooleanField(initial=False,required=False,widget=forms.CheckboxInput(attrs={
        'id':'same-address','class':'custom-control-input'
    }))
    save_info = forms.BooleanField(initial=False,required=False,widget=forms.CheckboxInput(attrs={
        'id':'save-info','class':'custom-control-input'
    }))
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)