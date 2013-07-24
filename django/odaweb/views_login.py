from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseServerError
from django.utils import simplejson
import dns.resolver
import bfd
import socket
import logging

logger = logging.getLogger(__name__)

def login(request):
    logger.info("Loggin In User")
    from django.contrib.auth import authenticate, login
    user = authenticate(username='john', password='johnpassword')
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponse()
        else:
            # Return a 'disabled account' error message
            raise Exception('User Has Disabled Account')
    else:
        raise Exception("Invalid Login")


def create_user(request):
    if request.method == 'GET':
        #render creeate user
        context = {}
        return render(request, 'login/create_user.djhtml', context)
    else:
        #process user form
        pass
    from django.contrib.auth.models import User
    user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    return HttpResponse(simplejson.dumps(user), mimetype='application/json')