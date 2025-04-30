from django.contrib import admin
from .models import *

admin.site.register(OrderTransaction)
admin.site.register(AdminTransaction)
admin.site.register(VendorTransaction)
admin.site.register(Payout)
admin.site.register(PaymentReference)
