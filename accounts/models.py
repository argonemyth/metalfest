from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from userena.models import UserenaBaseProfile
from userena.mail import send_mail
from userena import settings as userena_settings


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
        if (not self.mugshot) and self.facebook_id:
            return "http://graph.facebook.com/%s/picture?type=large" %  self.facebook_id
        elif (not self.mugshot) and self.profile_image_url:
            return self.profile_image_url
        else:
            return super(Profile, self).get_mugshot_url()

    def user_image(self):
        """Display usr image if available"""
        url = self.get_mugshot_url()
        if url:
            return '<img src="%s" style="height:80px; width: auto;">' % url
        else:
            return None
    user_image.allow_tags = True

    def send_welcome_email(self):
        """
        Sends an welcome email to new user.
        """

        context = {'site': Site.objects.get_current()}

        # Email to the new address
        subject = render_to_string('accounts/emails/welcome_email_subject.txt',
                                   context)
        subject = ''.join(subject.splitlines())

        if userena_settings.USERENA_HTML_EMAIL:
            message_html = render_to_string('accounts/emails/welcome_email_message.html',
                                            context)
        else:
            message_html = None

        if (not userena_settings.USERENA_HTML_EMAIL or not message_new_html or
            userena_settings.USERENA_USE_PLAIN_TEMPLATE):
            message = render_to_string('accounts/emails/welcome_email_message.txt',
                                       context)
        else:
            message = None

        send_mail(subject,
                  message,
                  message_html,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.user.email, ])


@receiver(post_save, sender=Profile)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        instance.send_welcome_email()


class SavedMap(models.Model):
    """
    This model will record each user's saved map.
    ```map_filters``` is a JSON string in a text field.
    """
    profile = models.ForeignKey(Profile, related_name='saved_maps')
    title = models.CharField(max_length=100)
    map_filters = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('saved map')
        verbose_name_plural = _('saved maps')
        unique_together = ('profile', 'title')
        get_latest_by = 'created_at'
        ordering = ['-created_at']

    def __unicode__(self):
        return self.title