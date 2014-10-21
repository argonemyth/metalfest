from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile
from django.db import models


class Profile(UserenaBaseProfile):
    GENDER_CHOICES = ( 
        (1, _('Male')),
        (2, _('Female')),
    ) 

    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='profile')
    gender = models.PositiveSmallIntegerField(_('gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True, null=True) 
    # Social networks
    twitter_id = models.CharField(max_length=100,
                                  blank=True, null=True)
    facebook_id = models.CharField(max_length=100,
                                   blank=True, null=True)