from django import forms
from userena.forms import AuthenticationForm, SignupFormOnlyEmail
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms_foundation.layout import Layout, Fieldset, Field, RowFluid, Row, Column, Div, ButtonHolder, Submit, HTML


class RegistrationForm(SignupFormOnlyEmail):
    first_name = forms.CharField(label=_(u'First name'),
                                 max_length=30,
                                 required=True)
    last_name = forms.CharField(label=_(u'Last name'),
                                max_length=30,
                                required=True)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            if self.fields[key].required:
                self.fields[key].widget.attrs["required"] = "" 

        self.helper = FormHelper()
        self.helper.form_tag = False # don't render form tag
        self.helper.layout = Layout(
            Row(Column(Field('email', placeholder="Email", css_class="small-12"))),
            Row(Column(Field('first_name', placeholder="First name", css_class="small-12"))),
            Row(Column(Field('last_name', placeholder="Last name", css_class="small-12"))),
            Row(Column(Field('password1', placeholder="Your password", css_class="small-12"))),
            Row(Column(Field('password2', placeholder="Repeat password", css_class="small-12"))),
            ButtonHolder(Submit('submit', _("Create Account"), css_class="secondary expand")),
        )

    def save(self):
        new_user = super(RegistrationForm, self).save()
        # Save first and last name
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()
        return new_user 


class SigninForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False # don't render form tag
        self.helper.layout = Layout(
            Row(Column(Field('identification', placeholder="Email", css_class="small-12"))),
            Row(Column(Field('password', placeholder="Password"))),
            # HTML('<label class="checkbox"><input type="checkbox" value="remember-me"/> Remember me for 2 weeks</label>')
            HTML('<input type="hidden" name="remember_me" value="remember-me">'),
            HTML('<input type="hidden" name="next" value="/#profile">'),
            ButtonHolder(Submit('submit', _("Sign In"), css_class="secondary expand")),
        )