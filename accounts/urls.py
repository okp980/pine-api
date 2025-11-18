from django.urls import path, include
from accounts.views import DriverOnlineStatusView

urlpatterns = [
    path("auth/", include("auth_kit.urls")),
    path(
        "driver/online-status/",
        DriverOnlineStatusView.as_view(),
        name="driver-online-status",
    ),
]
