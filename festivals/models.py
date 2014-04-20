from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
# from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings
from django.utils.encoding import smart_str

from geopy import geocoders
from uuslug import uuslug
from taggit.managers import TaggableManager

import logging
logger = logging.getLogger(__name__)

# from django.db.models import Q
#from django.utils.timezone import now

class Festival(models.Model):
    """ This model records the info for a metal festival """
    title = models.CharField(_("title"), max_length=255, unique=True)
    slug = models.CharField(max_length=255, unique=True, editable=False)
    description = models.TextField(_("description"), blank=True, null=True)
    start_date = models.DateField(_("start_date"), blank=True, null=True)
    end_date = models.DateField(_("end_date"), blank=True, null=True)
    url = models.URLField(_("URL"), blank=True, null=True)
    location = models.CharField(_("location"), max_length=300,
                                null=True, blank=True)
    city = models.ForeignKey('cities_light.City',
                             verbose_name=_('city'),
                             blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    blank=True, null=True)
    genres = TaggableManager(verbose_name=_("genres"), blank=True, 
                             help_text=_('A comma-separated list of genres'))

    class Meta:
        verbose_name = _('festival')
        verbose_name_plural = _('festivals')

    def __unicode__(self):
        return self.title  

    def get_geo_position(self):
        if (not self.location) or (not self.city):
            return None

        try:
            #g = geocoders.GoogleV3(resource='maps')
            g = geocoders.GoogleV3()
            address = "%s, %s" % (self.location, self.city)
            computed_address, (self.latitude, self.longitude) = g.geocode(smart_str(address),
                                                                          exactly_one=False)[0]
        except (UnboundLocalError, ValueError,geocoders.google.GQueryError):
            logger.warning("Can't find the lat, log for %s" % address)
            return None


    def save(self, ip=None, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        if (self.longitude is None) or (self.latitude is None):
            self.get_geo_position()
        super(Festival, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('festival-detail', args=[self.slug])