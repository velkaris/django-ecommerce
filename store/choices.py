from django.db import models
from django.utils.translation import gettext_lazy as _


# Choices
class Status(models.TextChoices):
    PUBLISHED = 'Published', _('Published')
    DRAFT = 'Draft', _('Draft')
    DISABLED = 'Disabled', _('Disabled')


class PaymentStatus(models.TextChoices):
    PAID = 'Paid', _('Paid')
    PROCESSING = 'Processing', _('Processing')
    FAILED = 'Failed', _('Failed')


class PaymentMethod(models.TextChoices):
    CASH = 'Cash', _('Cash')
    PAYPAL = 'PayPal', _('PayPal')
    STRIPE = 'Stripe', _('Stripe')
    FLUTTERWAVE = 'Flutterwave', _('Flutterwave')
    PAYSTACK = 'Paystack', _('Paystack')
    RAZORPAY = 'RazorPay', _('RazorPay')


class OrderStatus(models.TextChoices):
    PENDING = 'Pending', _('Pending')
    PROCESSING = 'Processing', _('Processing')
    SHIPPED = 'Shipped', _('Shipped')
    FULFILLED = 'Fulfilled', _('Fulfilled')
    CANCELLED = 'Cancelled', _('Cancelled')


class ShippingService(models.TextChoices):
    DHL = 'DHL', _('DHL')
    FEDEX = 'FedX', _('FedX')
    UPS = 'UPS', _('UPS')
    GIG_LOGISTICS = 'GIG Logistics', _('GIG Logistics')


class Rating(models.IntegerChoices):
    ONE_STAR = 1, _('★☆☆☆☆')
    TWO_STARS = 2, _('★★☆☆☆')
    THREE_STARS = 3, _('★★★☆☆')
    FOUR_STARS = 4, _('★★★★☆')
    FIVE_STARS = 5, _('★★★★★')