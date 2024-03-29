from django.contrib import admin
from django.db import models


def test_app_label():
    """
    Since Django 1.7 app_label while running tests is "elegant-django"
    instead of "tests" in Django < 1.7
    """
    try:
        return Book._meta.app_label
    except:
        return 'tests'


class Book(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id',)


class Album(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class BookAdmin(admin.ModelAdmin):
    list_filter = ('id', 'name',)
    list_display = ('id', 'name',)

    def elegant_row_attributes(self, obj, request):
        return {'class': 'elegant_row_attr_class-%s' % obj.name,
                'data': obj.pk,
                'data-request': request}

    def elegant_cell_attributes(self, obj, column):
        return {'class': 'elegant_cell_attr_class-%s-%s' % (column, obj.name),
                'data': obj.pk}


class AlbumAdmin(admin.ModelAdmin):
    def elegant_row_attributes(self, obj):
        """No request defined to test backward-compatibility"""
        return {'class': 'elegant_row_album_attr_class-%s' % obj.name,
                'data-album': obj.pk}


class User(models.Model):
    """
    Class to test menu marking as active if two apps have model with same name
    """
    name = models.CharField(max_length=64)


admin.site.register(Book, BookAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(User)
