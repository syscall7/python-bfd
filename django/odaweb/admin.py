from django.contrib import admin
from django import forms
from odaweb.models import *

class OdaFileForm(forms.ModelForm):
    class Meta:
        model = OdaFile
        fields = ['the_file']
        
class OdaFileAdmin(admin.ModelAdmin):
    form = OdaFileForm
    list_display = ('filename', 'filesize', 'hash', 'uuid', 'creation_date')
    def save_model(self, request, obj, form, change):
        obj.generate_values()
        obj.save()
        
class BinaryFileForm(forms.ModelForm):
    class Meta:
        model = BinaryFile
        fields = ['filename','filesize','the_file','hash']
        
class BinaryFileAdmin(admin.ModelAdmin):
    form = BinaryFileForm
    def save_model(self, request, obj, form, change):
        obj.generate_values()
        obj.save()

admin.site.register(OdaFile, OdaFileAdmin)
admin.site.register(BinaryFile, BinaryFileAdmin)