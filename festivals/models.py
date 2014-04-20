from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
# from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings

from uuslug import uuslug
from taggit.managers import TaggableManager
# from django.db.models import Q
#from django.utils.timezone import now

class Festival(models.Model):
    """ This model records the info for a metal festival """
    title = models.CharField(_("title"), max_length=255, unique=True)
    slug = models.CharField(max_length=255, unique=True, editable=False)
    description = models.TextField(_("description"), blank=True, null=True)
    start_date = models.DateField(_("start_date"))
    end_date = models.DateField(_("end_date"))
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

    def save(self, ip=None, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        super(Festival, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('festival-detail', args=[self.slug])