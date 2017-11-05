from django.conf.urls import include, url
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete

import oda.apps.users.urls as user_urls
import oda.apps.rest.urls as rest_urls


from oda.apps.odaweb import views2

admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'oda_python.views.home', name='home'),
    # url(r'^oda_python/', include('oda_python.foo.urls')),
    url(r'^$', RedirectView.as_view(url='/static/home/index.html')),
    url(r'^odaweb/run_hex.*$',  RedirectView.as_view(url='/odaweb/')),
    url(r'^odaweb/file_upload.*$', RedirectView.as_view(url='/odaweb/')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^superadmin/', include(admin.site.urls)),

    url(r'^odaweb/_owned_files$', views2.owned_files),
    url(r'^odaweb/_save$', views2.save),
    url(r'^odaweb/_upload$', views2.upload),
    url(r'^odaweb/comment$', views2.comment),
    url(r'^odaweb/_fileinfo$', views2.fileinfo),
    url(r'^odaweb/_instdoc$', views2.instdoc),
    url(r'^odaweb/_set', views2.set),
    url(r'^odaweb/optionsview', views2.options_form),
    url(r'^odaweb/_options', views2.show_options),
    url(r'^odaweb/_convert_to_data', views2.convert_to_data),
    url(r'^odaweb/_download', views2.download_text_listing),


    #User Dealing with URL
    url(r'^accounts/', include('allauth.urls')),
    url(r'^user/', include(user_urls.urlpatterns)),

    # url(r'^accounts/profile/$', lambda x: HttpResponseRedirect('/odaweb/')),
    #
    # url(r'^odaweb/login', 'oda.apps.users.views.login'),
    # url(r'^odaweb/logout', 'oda.apps.users.views.logout'),
    #
    # url(r'^accounts/password/reset$', password_reset, {
    #     'template_name': 'login/password_reset.djhtml',
    #     'email_template_name': 'login//password_reset_email.html'
    # }),
    # url(r'^accounts/password/reset/confirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)$', password_reset_confirm,
    #     {'template_name': 'login/password_reset_confirm.djhtml'}),
    # url(r'^accounts/password/reset/complete$', password_reset_complete,
    #     {'template_name': 'login/password_reset_complete.djhtml'}),
    # url(r'^accounts/password/reset_done$', password_reset_done,
    #     {'template_name': 'login/password_reset_done.djhtml'}),
    #
    # url(r'^odaweb/createuser', 'oda.apps.users.views.create_user'),

    # url(r'^odaweb/user/', include(user_urls.urlpatterns)),

    url(r'^odaweb/api/', include(rest_urls.urlpatterns)),

    #url(r'^odaweb/(?P<disassembly_id>\w{0,16})$$', 'oda.apps.odaweb.views2.index'),
    #url(r'^odaweb/(?P<disassembly_id>\w{0,16})/(?P<version>\w{0,16})$$', 'oda.apps.odaweb.views2.index'),

    url(r'^oda/connect/(?P<share_name>\w{0,16})$$', views2.connect, name='connect'),
    url(r'^odaweb/(?P<disassembly_id>\w{0,16})$$', views2.ace),
    url(r'^odaweb/(?P<disassembly_id>\w{0,16})/(?P<version>\w{0,16})$$', views2.ace, name="index"),

]
