from django.contrib import admin

# Register your models here.

from .models import Person, Location

class PersonAdmin(admin.ModelAdmin):
    list_display = ('name_last', 'name_first','name_middle')
    
    
# Registers
admin.site.register(Person, PersonAdmin)