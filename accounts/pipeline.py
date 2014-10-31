from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
# from django.shortcuts import redirect
# from django.contrib import messages

from userena.managers import ASSIGNED_PERMISSIONS
from guardian.shortcuts import assign_perm
from userena.utils import get_protocol
from social.exceptions import AuthAlreadyAssociated, AuthException, \
                              AuthForbidden
from accounts.models import Profile


def create_profile(backend, details, response, user=None, *args, **kwargs):
    """
    Create userna user profile if necessary
    """
    if not user:
        return

    profile, created = Profile.objects.get_or_create(user=user)
    if created:
        # Give permissions to view and change profile
        for perm in ASSIGNED_PERMISSIONS['profile']:
            assign_perm(perm[0], user, profile)
        # Give permissions to view and change user 
        for perm in ASSIGNED_PERMISSIONS['user']:
            assign_perm(perm[0], user, user)

    # if backend.name == 'twitter':
    #     profile.twitter_id = details['username']
    #     profile.profile_image_url = response.get('profile_image_url')
    #     profile.save()
        # profile.profile_image_url = response.get('profile_image_url_https')

    if backend.name == 'facebook' and not profile.facebook_id:
        profile.facebook_id = response.get('id')
        gender = response.get('gender')
        if gender == 'female':
            profile.gender = 2
        if gender == 'male':
            profile.gender = 1
        profile.save()

    return { 'profile': profile }