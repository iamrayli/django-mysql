from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.CafeAdmin)
admin.site.register(models.UserInfo)
admin.site.register(models.Comp)
admin.site.register(models.RcgRecord)
admin.site.register(models.Area)
admin.site.register(models.PayRecord)
