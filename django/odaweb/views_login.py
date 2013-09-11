from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseServerError
from django.core import serializers
from django import forms
from django.db import IntegrityError
import logging
from django.contrib.auth import authenticate
import django.contrib.auth
from django.contrib.auth.models import User
logger = logging.getLogger(__name__)

class UserForm(forms.Form):
    username = forms.CharField(max_length=32, min_length=4, required=True)
    password = forms.CharField(max_length=32, min_length=6, required=True)

class CreateUser(UserForm):
    email = forms.EmailField(required=True)
    password2 = forms.CharField(max_length=32, min_length=6, required=True)

    def clean(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")

        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(u'Email already registered.')

        return self.cleaned_data

def create_context():
    return {
        'auth_providers': ['google', 'facebook', 'twitter']
    }

def logout(request):
    logger.debug('Logging Out %s' % request.user.username)
    django.contrib.auth.logout(request)
    return redirect('/odaweb/')

def login(request):
    if request.method == 'GET':
        #render creeate user
        context = create_context()

        return render(request, 'login/login.djhtml', context)
    else:
        form = UserForm(request.POST)
        if form.is_valid(): # All validation rules pass

            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    logger.info("Loggin In User %s" % form.cleaned_data['username'])
                    django.contrib.auth.login(request, user)
                    return redirect('/odaweb/')
                else:
                    # Return a 'disabled account' error message
                    raise Exception('User Has Disabled Account')

    return render(request, 'login/login.djhtml', {'error': 'Invalid Username/Password'})



def create_user(request):
    if request.method == 'GET':
        #render creeate user
        context = create_context()
        return render(request, 'login/create_user.djhtml', context)
    else:
        form = CreateUser(request.POST)
        if form.is_valid(): # All validation rules pass
            logger.info("Creating User %s" % form.cleaned_data['username'])

            try:
                user_model = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
            except IntegrityError:
                return render(request, 'login/create_user.djhtml', {'error': "Username already taken"})
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            logger.info("Loggin In User %s" % form.cleaned_data['username'])
            django.contrib.auth.login(request, user)
            return redirect('/odaweb/')
            #return HttpResponse(serializers.serialize('json', [user]), mimetype='application/json')
        else:
            return render(request, 'login/create_user.djhtml', {'form': form})
