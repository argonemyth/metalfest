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
    profile_image_url = models.URLField(null=True, blank=True)


    def get_mugshot_url(self):
        """
        Returns the image containing the mugshot for the user.

        The mugshot can be a uploaded image or a gravatar or a social network avatar.

        Gravatar functionality will only be used when
        ``USERENA_MUGSHOT_GRAVATAR`` is set to ``True``.

        Facebook avatar will only be used when facebook_id is valid.
        """
        if (not self.mugshot) and self.profile_image_url:
            return self.profile_image_url
        elif (not self.mugshot) and self.facebook_id:
            return get_facebook_avatar(self.facebook_id)
        else:
            return super(Profile, self).get_mugshot_url()