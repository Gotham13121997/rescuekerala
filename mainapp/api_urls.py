from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'camps', api_views.RescueCampViewSet)
router.register(r'persons', api_views.PersonViewSet)

urlpatterns = [
    path('camplist/', api_views.CampList.as_view(), name='api_camplist'),
]

urlpatterns += router.urls
