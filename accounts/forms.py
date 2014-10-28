from django import forms
from userena.forms import AuthenticationForm, SignupForm
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms_foundation.layout import Layout, Fieldset, Field, RowFluid, Row, Column, Div, ButtonHolder, Submit, HTML


class RegistrationForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            if self.fields[key].required:
                self.fields[key].widget.attrs["required"] = "" 

        self.helper = FormHelper()
        self.helper.form_tag = False # don't render form tag
        self.helper.layout = Layout(
            Row(Column(Field('username', placeholder="Username", css_class="no-bottom-radius small-12"))),
            Row(Column(Field('email', placeholder="Email", css_class="no-bottom-radius small-12"))),
            Row(Column(Field('password1', placeholder="Your password", css_class="no-bottom-radius small-12"))),
            Row(Column(Field('password2', placeholder="Repeat password", css_class="no-bottom-radius small-12"))),
            ButtonHolder(Submit('submit', _("Create Account"), css_class="secondary expand")),
        )


class SigninForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False # don't render form tag
        self.helper.layout = Layout(
            Row(Column(Field('identification', placeholder="Username or Email", css_class="no-bottom-radius small-12"))),
            Row(Column(Field('password', placeholder="Password", css_class="no-top-radius"))),
            # HTML('<label class="checkbox"><input type="checkbox" value="remember-me"/> Remember me for 2 weeks</label>')
            HTML('<input type="hidden" name="remember_me" value="remember-me">'),
            HTML('<input type="hidden" name="next" value="/#profile">'),
            ButtonHolder(Submit('submit', _("Sign In"), css_class="secondary expand")),
        )