from django.contrib import admin
from tagstar.models import *

class AdminTag(admin.ModelAdmin):
    list_display = ('name', 'count')

admin.site.register( Tag, AdminTag )
admin.site.register( Item )

