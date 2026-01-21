from rest_framework.routers import DefaultRouter

from .views import LocalizationViewSet, OfficeViewSet

router = DefaultRouter()
router.register("localizations", LocalizationViewSet, basename="localization")
router.register("offices", OfficeViewSet, basename="office")

urlpatterns = router.urls
