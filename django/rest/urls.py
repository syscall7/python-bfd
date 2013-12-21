from django.conf.urls import patterns, url, include
from rest_framework import routers
from rest import views

router = routers.DefaultRouter()
router.register(r'masters', views.OdaMasterViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'sections', views.SectionsViewSet, base_name="sections ")
router.register(r'parcels', views.ParcelsViewSet, base_name="parcels")
router.register(r'displayunits', views.DisplayUnitsViewSet, base_name="displayunits")
router.register(r'strings', views.StringsViewSet, base_name="strings")
router.register(r'symbols', views.SymbolsViewSet, base_name="symbols")
router.register(r'functions', views.FunctionViewSet, base_name="functions")
router.register(r'labels', views.LabelsViewSet, base_name='labels')
router.register(r'binarystrings', views.BinaryStringViewSet, base_name="binarystrings")
router.register(r'find', views.FindViewSet, base_name="find")

#router.register(r'superchunks', views.SuperChunksViewSet, base_name="superchunks")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))

)