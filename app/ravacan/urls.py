from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_urls = [
    path('bom/', include('bom.urls')),

    path('schema/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(api_urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('__debug__/', include('debug_toolbar.urls')),
]
