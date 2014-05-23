from django import forms
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms_foundation.layout import Layout, Fieldset, Field, RowFluid, Row, Column, Div, ButtonHolder, Submit, HTML

from festivals.fields import (CitySelect2Field,
                              CitySelect2MultipleField,
                              CountrySelect2Field)
from festivals.models import Festival

INFO_TYPES = (
  ("url", _("URL")),
  ("date", _("Date")),
  ("location", _("Location")),
  ("lineup",_("Linup"))
)

class FestivalAdminForm(forms.ModelForm):
  city = CitySelect2Field(required=False)

  class Meta:
    model = Festival


class FestivalReportErrorForm(forms.Form):
  info_type = forms.MultipleChoiceField(required=True, choices=INFO_TYPES,
                                        widget=forms.CheckboxSelectMultiple,
                                        label=_("What info are not correct?"))
  support = forms.CharField(max_length=1000, widget=forms.Textarea,
                            label=_("What's the correct data? / Where can we\
                                    find the correct data"))

  def __init__(self, *args, **kwargs):
    super(FestivalReportErrorForm, self).__init__(*args, **kwargs)
    self.helper = FormHelper()
    self.helper.form_tag = False
    self.helper.layout = Layout(
      Row(Column(Field('info_type'), css_class="small-11")),
      Row(Column(Field('support'), css_class="small-12")),
      ButtonHolder(Submit('submit', _("Send"), css_class="expand")),
    )



class FilterForm(forms.Form):
    """
    Not needed anymore The form to filter festivals.
    """
    start_month = forms.CharField(
                    widget=forms.TextInput(attrs={'data-slider-min': '0',
                                                  'data-slider-max': '12',
                                                  'data-slider-step': '1',
                                                  'data-slider-value': '[0,12]',
                                                  'value': ''}),
                    label=_("start month"), required=False)
    end_month = forms.CharField(
                    widget=forms.TextInput(attrs={'data-slider-min': '0',
                                                  'data-slider-max': '12',
                                                  'data-slider-step': '1',
                                                  'data-slider-value': '[0,12]',
                                                  'value': ''}),
                    label=_("end month"), required=False)

