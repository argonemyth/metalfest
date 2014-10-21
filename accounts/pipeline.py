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
    try:
        profile = user.get_profile()
    except Profile.DoesNotExist:
        pass
    else:
        return { 'profile': profile}

    print "Details: ", details
    print "Response: ", response 
    print "Backend: ", backend.name

    #return { 'profile': Profile.objects.get_or_create(user=user)[0] }
    profile, created = Profile.objects.get_or_create(user=user)
    if created:
        # Give permissions to view and change profile
        for perm in ASSIGNED_PERMISSIONS['profile']:
            assign_perm(perm[0], user, profile)
        # Give permissions to view and change user 
        for perm in ASSIGNED_PERMISSIONS['user']:
            assign_perm(perm[0], user, user)

    if backend.name == 'twitter':
        profile.twitter_id = details['username']
        profile.profile_image_url = response.get('profile_image_url')
        profile.save()
        # profile.profile_image_url = response.get('profile_image_url_https')

    if backend.name == 'facebook':
        profile.facebook_id = response.get('id')
        gender = response.get('gender')
        if gender == 'female':
            profile.gender = 2
        if gender == 'male':
            profile.gender = 1
        profile.save()

    # if created and (user.password == u'!'):
    #     # generate password and send out email notification
    #     password = User.objects.make_random_password()
    #     user.set_password(password)
    #     if user.email:
    #         context = {'user': profile.get_full_name_or_username(),
    #                    'username': user.username,
    #                    'password': password,
    #                    'email': user.email,
    #                    'protocol': get_protocol(),
    #                    'site': Site.objects.get_current()}
    #         subject = render_to_string('accounts/password_notification_subject.txt',
    #                                    context)
    #         subject = ''.join(subject.splitlines())

    #         message = render_to_string('accounts/password_notification_message.txt',
    #                                    context)
    #         send_mail(subject,
    #                   message,
    #                   settings.DEFAULT_FROM_EMAIL,
    #                   [user.email])

    return { 'profile': profile }