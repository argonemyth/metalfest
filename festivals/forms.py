from django import forms
from django.utils.translation import ugettext as _

from festivals.fields import (CitySelect2Field,
                              CitySelect2MultipleField,
                              CountrySelect2Field)
from festivals.models import Festival


class FestivalAdminForm(forms.ModelForm):
  city = CitySelect2Field(required=False)

  class Meta:
    model = Festival


class FilterForm(forms.Form):
    """
    The form to filter festivals.
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