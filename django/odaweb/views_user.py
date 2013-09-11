from django.conf.urls import url, patterns
from django.http import HttpResponse

urlpatterns = patterns('',
    url(r'files/$', 'odaweb.views_user.files')
)


def files(request):
    return HttpResponse('user files')