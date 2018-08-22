from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'camps', api_views.RescueCampViewSet)
router.register(r'persons', api_views.PersonViewSet)

urlpatterns = [
    path('camplist/', api_views.CampList.as_view(), name='api_camplist'),
    path('request_update/', api_views.request_update_list, name='api_request_update'),
    path('kerala_local_bodies/', api_views.get_kerala_local_bodies, name='api_kerala_local_bodies'),
]

urlpatterns += router.urls
