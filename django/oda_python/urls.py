from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'oda_python.views.home', name='home'),
    # url(r'^oda_python/', include('oda_python.foo.urls')),
    (r'^$', lambda x: HttpResponseRedirect('/odaweb/')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^odaweb/run_hex$', 'odaweb.views.run_hex'),
    url(r'^odaweb/run_hex/(?P<snippet_id>[\w-]+)$', 'odaweb.views.run_hex'),
    url(r'^odaweb/file_upload', 'odaweb.views.file_upload'),
    url(r'^odaweb/clear$', 'odaweb.views.clear'),
    url(r'^odaweb/disassemble/uploadHex$', 'odaweb.views.upload_hex'),
    url(r'^odaweb/disassemble/showOptions$', 'odaweb.views.show_options'),
    url(r'^disassemble/uploadFile$', 'odaweb.views.upload_file'),
    url(r'^disassemble/checkExisting', 'odaweb.views.check_existing'),
    url(r'^odaweb/disassemble/(?P<file_id>[\w-]+)$', 'odaweb.views.disassemble'),
    url(r'^odaweb/download/(?P<file_id>[\w-]+)$', 'odaweb.views.download'),
    url(r'^odaweb/update_disassembly/(?P<file_id>[\w-]+)$', 'odaweb.views.update_disassembly'),
    url(r'^odaweb/refresh_disassembly/(?P<file_id>[\w-]+)$', 'odaweb.views.refresh_disassembly'),
    #url(r'^odaweb/comment/(?P<file_id>[\w-]+)/(?P<offset>[0-9A-Fa-f]{8})$', 'odaweb.views.comment'),

    url(r'^odaweb/_owned_files$', 'odaweb.views2.owned_files'),
    url(r'^odaweb/_save$', 'odaweb.views2.save'),
    url(r'^odaweb/_upload$', 'odaweb.views2.upload'),
    url(r'^odaweb/_refresh$', 'odaweb.views2.refresh_disassembly'),
    url(r'^odaweb/_partial_refresh$', 'odaweb.views2.partial_refresh_disassembly'),
    url(r'^odaweb/comment$', 'odaweb.views2.comment'),
    url(r'^odaweb/_symbols$', 'odaweb.views2.symbols'),
    url(r'^odaweb/_strings$', 'odaweb.views2.strings'),
    url(r'^odaweb/_sections$', 'odaweb.views2.sections'),
    url(r'^odaweb/_fileinfo$', 'odaweb.views2.fileinfo'),
    url(r'^odaweb/_instdoc$', 'odaweb.views2.instdoc'),
    url(r'^odaweb/_set', 'odaweb.views2.set'),
    url(r'^odaweb/_options', 'odaweb.views2.show_options'),
    url(r'^odaweb/(?P<disassembly_id>\w{0,16})$$', 'odaweb.views2.index'),
)
