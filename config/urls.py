"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # Api urls
    path('api/', include('apps.about.api.urls')),
    path('api/', include('apps.authentication.api.urls')),
    path('api/', include('apps.extra.api.urls')),
    path('api/', include('apps.location.api.urls')),
    path('api/', include('apps.main.api.urls')),
    path('api/', include('apps.notification.api.urls')),
    path('api/', include('apps.subscription.api.urls')),
    path('api/', include('apps.trading.api.urls')),
]

urlpatterns += i18n_patterns(
    path('', include('apps.about.urls')),
    path('', include('apps.authentication.urls')),
    path('', include('apps.extra.urls')),
    path('', include('apps.location.urls')),
    path('', include('apps.main.urls')),
    path('', include('apps.notification.urls')),
    path('', include('apps.stories.urls')),
    path('', include('apps.subscription.urls')),
    path('', include('apps.trading.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls'))
    ]