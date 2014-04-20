from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    url(r'files/$', 'users.views.files')
)