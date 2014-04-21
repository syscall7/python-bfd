from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    url(r'files/$', 'oda.apps.users.views.files')
)