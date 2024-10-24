from django.db import models
from django.core.exceptions import ValidationError
from store.choices import Status, PaymentStatus, PaymentMethod, OrderStatus, ShippingService, Rating
from django.utils.text import slugify
import shortuuid
import uuid
from shortuuid.django_fields import ShortUUIDField
from django_ckeditor_5.fields import CKEditor5Field
from userauths import models as user_models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Represents a product category in the online store.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category/images', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    date = models.DateField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)    

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(models.Model):
    """
    Represents a product in the online store.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='product/images', default='default-product.jpg')
    description = CKEditor5Field('Description', config_name='full')
    short_inf = CKEditor5Field('Short Information', config_name='full')

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Sale Price')
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Regular Price')

    stock = models.PositiveIntegerField(default=10)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Shipping Amount')

    status = models.CharField(max_length=50, choices=Status.choices, default=Status.DRAFT)
    featured = models.BooleanField(default=False, verbose_name='Marketplace Featured')

    type = models.CharField(max_length=100, default='Organic')
    sku = ShortUUIDField(unique=True, max_length=10, length=5, alphabet='1234567890')
    slug = models.SlugField(null=True, blank=True)

    life = models.PositiveIntegerField(default=10)
    date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.pk and not self.slug:
            self.slug = slugify(self.name) + '-' + str(shortuuid.uuid().lower()[:2])
        super(Product, self).save(*args, **kwargs)
    
    def average_rating_percentage(self):
        avg = Review.objects.filter(product=self).aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        return (avg * 20) if avg is not None else 0
    
    def average_rating(self):
        avg = Review.objects.filter(product=self).aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        return avg if avg is not None else 0
    
    def reviews(self):
        return Review.objects.filter(product=self)
    
    def gallery(self):
        return Gallery.objects.filter(product=self)
    
    def variants(self):
        return Variant.objects.filter(product=self)
    
    def vendor_orders(self):
        return OrderItem.objects.filter(product=self, vendor=self.vendor)

    def __str__(self):
        return self.name
    

class Variant(models.Model):
    """
    Represents a variant of a product, such as size or color.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Variant Name')

    def items(self):
        return VariantItem.objects.filter(variant=self)
    
    def __str__(self):
        return self.name
    

class VariantItem(models.Model):
    """
    Represents an item belonging to a specific variant of a product.
    """
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='variant_items')
    title = models.CharField(max_length=1000, verbose_name='Variant Title')
    description = models.CharField(max_length=1000, verbose_name='Item Description', null=True, blank=True)

    def __str__(self):
        return f'{self.variant.name} - {self.title}'
    

class Gallery(models.Model):
    """
    Represents a gallery of images for a product.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/images', default='default-gallery.jpg')
    
    class Meta:
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"

    def __str__(self):
        return f'{self.product.name} - image'
    

class Cart(models.Model):
    """
    Represents a shopping cart for a user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=0)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id} - {self.product.name}'
    

class Coupon(models.Model):
    """
    Represents a discount coupon that can be applied to orders.
    """
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    code = models.CharField(max_length=50)
    discount = models.IntegerField(default=1)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if not (0 < self.discount <= 100):
            raise ValidationError(_('Discount must be between 1 and 100.'))

    def __str__(self):
        return self.code


class Order(models.Model):
    """
    Represents an order placed by a customer.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vendor = models.ManyToManyField(user_models.User, related_name='order_vendor')
    customer = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_status = models.CharField(max_length=100, choices=PaymentStatus.choices, default=PaymentStatus.PROCESSING)
    payment_method = models.CharField(max_length=100, choices=PaymentMethod.choices)
    order_status = models.CharField(max_length=100, choices=OrderStatus.choices, default=OrderStatus.PENDING)

    initial_total = models.DecimalField(max_digits=10, decimal_places=2, help_text='The original total before discounts')
    saved = models.DecimalField(max_digits=10, decimal_places=2, help_text='Amount saved with coupon')

    # address = models.ForeignKey('customer.Address', on_delete=models.SET_NULL, null=True, blank=True, related_name='order')
    coupons = models.ManyToManyField(Coupon)

    date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-date']

    # Get related order items
    def order_items(self):
        return OrderItem.objects.filter(order=self)

    def __str__(self):
        return f'Order {self.id} - {self.customer.email if self.customer else "Guest"}'
    

class OrderItem(models.Model):
    """
    Representing individual items within an order
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=100, choices=OrderStatus.choices, default='Pending')
    
    shipping_service = models.CharField(max_length=100, choices=ShippingService.choices, default=None)
    tracking_id = models.CharField(max_length=100, default=None, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(default=0)

    color = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    initial_total = models.DecimalField(max_digits=10, decimal_places=2, help_text='Grand Total of all amount')
    saved = models.DecimalField(max_digits=10, decimal_places=2, help_text='Saved Amount')

    coupon = models.ManyToManyField(Coupon)
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_order_items')
    applied_coupon = models.BooleanField(default=False)

    date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "OrderItem"
        verbose_name_plural = "OrderItems"
        ordering = ['-date']

    def order_id(self):
        return f'{self.order.id}'

    def __str__(self):
        return f'{self.id} - {self.product.name}'
    

class Review(models.Model):
    """
    Representing customer reviews for products
    """
    user = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    rating = models.IntegerField(choices=Rating.choices, default=None)
    active = models.BooleanField(default=False)

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f'{self.user.username} reviews on {self.product.name}'
    
