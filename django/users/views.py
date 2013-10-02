from django.shortcuts import render
from django.template import Context
from odaweb.models import OdaMaster


def create_user_context(context={}):
    return Context(context)


def files(request):
    context = {
        'masters': OdaMaster.objects.filter(owner=request.user, copy = None)
    }
    return render(request, 'files.djhtml', create_user_context(context))