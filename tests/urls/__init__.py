from django.contrib import admin
from django.urls import include

admin.autodiscover()

try:
    # Django 2.0+
    from django.urls import path

    urlpatterns = [
        path(r'admin/', admin.site.urls),
    ]
except ImportError:
    try:
        from django.conf.urls import patterns, url

        urlpatterns = patterns(
            '',
            # Examples for custom menu
            url(r'^admin/', include(admin.site.urls)),
        )
    except ImportError:  # Django 1.10+
        urlpatterns = [
            url(r'^admin/', include(admin.site.urls)),
        ]
