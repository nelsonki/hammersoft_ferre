from django.contrib import admin
from core.erp.models import *
# Register your models here.

admin.site.register(Category)
admin.site.register(StoreProd)
admin.site.register(Client)
admin.site.register(Product)
admin.site.register(ProdCombo)
admin.site.register(DetProdCombo)
admin.site.register(StoreProdStock)
admin.site.register(Output)
admin.site.register(DetOutput)
admin.site.register(Order)
admin.site.register(DetOrder)
admin.site.register(Input)
admin.site.register(DetInput)
admin.site.register(Movement)
admin.site.register(DetMov)
admin.site.register(Inventory)
admin.site.register(Config)
admin.site.register(Adjustment)
admin.site.register(DetAdjustment)