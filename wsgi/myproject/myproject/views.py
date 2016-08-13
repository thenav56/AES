from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import loginForm


def index(request):
    return HttpResponseRedirect(reverse('essay:index'))
    # return render(request, 'myproject/index.html')


def app_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('essay:index'))

    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    # Redirect to a success page.
                    login(request, user)
                    messages.add_message(request, messages.INFO, 'Logged In')
                    return HttpResponseRedirect(reverse('essay:index'))
                else:
                    # Return a 'disabled account' error message
                    messages.add_message(request, messages.ERROR, 'Account\
                                         is disabled')
            else:
                messages.add_message(request, messages.WARNING, 'Password or\
                                     Username didn\'t match')
    else:
        form = loginForm()
    return render(request, 'login.html', {'form': form})

def app_logout(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'Logged Out')
    return HttpResponseRedirect(reverse('essay:index'))
