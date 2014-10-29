from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME

import json

from userena.decorators import secure_required
from userena import signals as userena_signals
from userena import settings as userena_settings

from accounts.models import Profile
from accounts.forms import SigninForm, RegistrationForm
from accounts.utils import errors_to_json


def my_profile(request, extra_context=None, **kwargs):
    """
    Detailed view of current user.
    """
    print "in my profile view"
    if not request.user.is_authenticated():
        # return login template
        print "user is not authenticated"
        signin_form = SigninForm()
        signup_form = RegistrationForm()
        return render(request, 'accounts/signin.html', {'signin_form': signin_form,
                                                        'signup_form': signup_form})

    try:
        profile = request.user.get_profile()
    except Profile.DoesNotExist:
        # return error
        pass

    return render(request, 'accounts/my_profile.html', {'profile': profile})


@secure_required
def signup(request, signup_form=RegistrationForm,
           template_name='userena/signup_form.html', success_url=None,
           extra_context=None):
    """
    An ajax version of django-userena signup
    """
    # If signup is disabled, return 403
    # if userena_settings.USERENA_DISABLE_SIGNUP:
    #     raise PermissionDenied

    # If no usernames are wanted and the default form is used, fallback to the
    # default form that doesn't display to enter the username.
    # if userena_settings.USERENA_WITHOUT_USERNAMES and (signup_form == SignupForm):
    #     signup_form = SignupFormOnlyEmail

    form = signup_form()

    if request.method == 'POST' and request.is_ajax():
        form = signup_form(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Send the signup complete signal
            userena_signals.signup_complete.send(sender=None,
                                                 user=user)


            # if success_url: redirect_to = success_url
            # else: redirect_to = reverse('userena_signup_complete',
            #                             kwargs={'username': user.username})

            # A new signed user should logout the old one.
            if request.user.is_authenticated():
                logout(request)

            if (userena_settings.USERENA_SIGNIN_AFTER_SIGNUP and
                not userena_settings.USERENA_ACTIVATION_REQUIRED):
                    user = authenticate(identification=user.email, check_password=False)
                    login(request, user)

            return HttpResponse(json.dumps({"status": "success"}), content_type='text/json')
        else:
            print errors_to_json(form.errors, True)
            return HttpResponse(errors_to_json(form.errors, True), content_type='text/json')

    return redirect('/')

    # if not extra_context: extra_context = dict()
    # extra_context['form'] = form
    # return ExtraContextTemplateView.as_view(template_name=template_name,
    #                                         extra_context=extra_context)(request)