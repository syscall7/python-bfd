from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from django.core.urlresolvers import reverse

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'oda_python.views.home', name='home'),
    # url(r'^oda_python/', include('oda_python.foo.urls')),
    (r'^$', lambda x: HttpResponseRedirect('/odaweb/')),
    (r'^odaweb/run_hex.*$', lambda x: HttpResponseRedirect('/odaweb/')),
    (r'^odaweb/file_upload.*$', lambda x: HttpResponseRedirect('/odaweb/')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),

    url(r'^odaweb/_owned_files$', 'odaweb.views2.owned_files'),
    url(r'^odaweb/_save$', 'odaweb.views2.save'),
    url(r'^odaweb/_upload$', 'odaweb.views2.upload'),
    url(r'^odaweb/_refresh$', 'odaweb.views2.refresh_disassembly'),
    url(r'^odaweb/_refreshHex', 'odaweb.views2.refresh_hex'),
    url(r'^odaweb/_partial_refresh$', 'odaweb.views2.partial_refresh_disassembly'),
    url(r'^odaweb/_partial_refreshHex', 'odaweb.views2.partial_refresh_hex'),
    url(r'^odaweb/comment$', 'odaweb.views2.comment'),
    url(r'^odaweb/_symbols$', 'odaweb.views2.symbols'),
    url(r'^odaweb/_strings$', 'odaweb.views2.strings'),
    url(r'^odaweb/_sections$', 'odaweb.views2.sections'),
    url(r'^odaweb/_fileinfo$', 'odaweb.views2.fileinfo'),
    url(r'^odaweb/_instdoc$', 'odaweb.views2.instdoc'),
    url(r'^odaweb/_set', 'odaweb.views2.set'),
    url(r'^odaweb/_options', 'odaweb.views2.show_options'),


    #User Dealing with URL
    url(r'^odaweb/login', 'odaweb.views_login.login'),
    url(r'^odaweb/logout', 'odaweb.views_login.logout'),

    url(r'^accounts/password/reset$', password_reset, {
        'template_name': 'login/password_reset.djhtml'
    }),
    url(r'^accounts/password/reset/confirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)$', password_reset_confirm,
        {'template_name': 'login/password_reset_confirm.djhtml'}),
    url(r'^accounts/password/reset/complete$', password_reset_complete,
        {'template_name': 'login/password_reset_complete.djhtml'}),
    url(r'^accounts/password/reset_done$', password_reset_done,
        {'template_name': 'login/password_reset_done.djhtml'}),

    url(r'^odaweb/createuser', 'odaweb.views_login.create_user'),



    url(r'^odaweb/(?P<disassembly_id>\w{0,16})$$', 'odaweb.views2.index')
)
