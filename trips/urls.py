from django.urls import path, include
from rest_framework.routers import DefaultRouter
from trips.views import TripViewSet

router = DefaultRouter()
router.register(r"trips", TripViewSet, basename="trip")

urlpatterns = router.urls
