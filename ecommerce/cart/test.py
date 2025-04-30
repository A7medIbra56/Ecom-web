import math
from decimal import Decimal

commission_rate = 1
effective_vendor_amount = round(176.9233 * (100 - commission_rate) / 100, 2)
print(effective_vendor_amount)