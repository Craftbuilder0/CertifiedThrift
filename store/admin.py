from django.contrib import admin
from store.models import *

# Register your models here.
admin.site.register(products)
admin.site.register(category)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)