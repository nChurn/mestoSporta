from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Category)
admin.site.register(City)
admin.site.register(District)
admin.site.register(Metro)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
	ordering = ['is_active']


admin.site.register(SectionPhoto)
admin.site.register(Traning)
admin.site.register(User)