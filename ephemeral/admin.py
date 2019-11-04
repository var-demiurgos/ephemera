from django.contrib import admin
from .models import Ephemera, NGList, EphemeraURL, EphemeraDomain
# Register your models here.

admin.site.register(Ephemera)
admin.site.register(EphemeraDomain)
admin.site.register(EphemeraURL)
admin.site.register(NGList)