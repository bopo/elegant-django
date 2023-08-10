from django.contrib import admin
from django.urls import include, path

admin.autodiscover()

urlpatterns = ('',
               # Examples for custom menu
               path(r'', include(admin.site.urls)),
               )
