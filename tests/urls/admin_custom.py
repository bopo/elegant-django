from django.urls import include, path
from django.contrib import admin

admin.autodiscover()

urlpatterns = ('',
    # Examples for custom menu
    path('foo/bar/', include(admin.site.urls)),
)
