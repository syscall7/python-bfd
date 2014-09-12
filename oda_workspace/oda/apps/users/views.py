import json
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import Context
from oda.apps.odaweb.models import OdaMaster
from django import forms
import django.contrib.auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import logging


logger = logging.getLogger(__name__)

def create_user_context(context={}):
    return Context(context)


def files(request):
    context = {
        'masters': OdaMaster.objects.filter(owner=request.user, copy=None).order_by('-creation_date')[:25]
    }
    return render(request, 'files.djhtml', create_user_context(context))