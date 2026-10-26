from captcha.fields import ReCaptchaField
from django import forms


class AllauthSignupForm(forms.Form):
    captcha = ReCaptchaField()

    def signup(self, request, user):
        """Required, or else it throws deprecation warnings"""
        pass

    field_order = ["email", "password1", "password2", "captcha"]
