from django.shortcuts import render

from accounts.models import Profile
from accounts.forms import SigninForm

def my_profile(request, extra_context=None, **kwargs):
    """
    Detailed view of current user.
    """
    print "in my profile view"
    if not request.user.is_authenticated():
        # return login template
        print "user is not authenticated"
        signin_form = SigninForm()
        return render(request, 'accounts/signin.html', {'signin_form': signin_form})

    try:
        profile = request.user.get_profile()
    except Profile.DoesNotExist:
        # return error
        pass

    return render(request, 'accounts/my_profile.html', {'profile': profile})
