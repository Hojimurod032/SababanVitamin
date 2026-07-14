import re
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField

from apps.models import User, Order


class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'password']

    def __init__(self, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(**kwargs)

    def clean(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_number = re.sub(r'\D', "", phone_number)
        password = self.cleaned_data.get('password')

        user_data = User.objects.filter(phone_number=phone_number).first()
        if not user_data:
            raise ValidationError("Bundey telefon raqam topilmadi")
        if not check_password(password, user_data.password):
            raise ValidationError("Sizning parolingiz xato")

        login(self.request, user_data)


class RegisterForm(ModelForm):
    conf_password = CharField(max_length=55)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'password', 'conf_password']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_number = re.sub(r'\D', "", phone_number)
        user_data = User.objects.filter(phone_number=phone_number).first()
        if user_data:
            raise ValidationError("Kechirasiz bundey raqam allaqachon mavjud")

        return phone_number

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return make_password(password)

    def clean_conf_password(self):
        conf_password = self.cleaned_data.get('conf_password')
        password = self.data.get('password')
        if conf_password != password:
            raise ValidationError("Kechirasiz sizning parolingiz bir biriga mos kelmadi")


class CreateOrderForm(ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'second_number',
            'region',
            'city',
            'address',
            'desc',
            'payment_check',
            'quanty',
            'promo_code',
            'discount_amount'
        ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number is None:
            raise ValidationError('Iltimos telefon raqamni kiriting')

        return phone_number

    def clean_payment_check(self):
        payment_check = self.cleaned_data.get('payment_check')
        if payment_check is None:
            raise ValidationError('Iltimos tolov chekini kiriting')

        return payment_check
