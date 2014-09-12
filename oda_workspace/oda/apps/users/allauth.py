from __future__ import absolute_import
from allauth.account.adapter import DefaultAccountAdapter

__author__ = 'davis'

class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return "/"
