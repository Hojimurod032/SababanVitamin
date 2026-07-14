from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from apps.views import CheckPromoView
from sababan import settings

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n'), name="set_language"),
    path('check-promo/', CheckPromoView.as_view(), name='check_promo'),
]

urlpatterns += i18n_patterns(
    path('', include("apps.urls")),
    path('admin/', admin.site.urls),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)