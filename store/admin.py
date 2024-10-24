from django.contrib import admin
from store import models as store_model


class GalleryInline(admin.TabularInline):
    model = store_model.Gallery


class VariantInline(admin.TabularInline):
    model = store_model.Variant


class VariantItemInline(admin.TabularInline):
    model = store_model.VariantItem


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'image']  # Исправлено здесь
    list_editable = ['image']
    prepopulated_fields = {'slug': ('title',)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'vendor', 'price', 'regular_price', 'status', 'featured', 'stock', 'date']  # Исправлено здесь
    search_fields = ['name', 'category__title']
    list_filter = ['status', 'featured', 'category']
    inlines = [GalleryInline, VariantInline]  # Исправлено здесь
    prepopulated_fields = {'slug': ('name',)}


class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name']  # Убедитесь, что status и featured действительно существуют в модели Variant
    search_fields = ['product__name', 'name']
    list_filter = ['product__category']  # Убедитесь, что используется корректное поле
    inlines = [VariantItemInline]


class VariantItemAdmin(admin.ModelAdmin):
    list_display = ['variant', 'title', 'description']  # Исправлено здесь
    search_fields = ['variant__name', 'title']


class GalleryAdmin(admin.ModelAdmin):
    list_display = ['product', 'id']  # Исправлено здесь, используем 'id' вместо 'gallery_id'
    search_fields = ['product__name', 'title']


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'qty', 'price', 'total', 'date']  # Исправлено здесь, используем 'id' вместо 'cart_id'
    search_fields = ['id', 'product__name', 'user__username']
    list_filter = ['date', 'product']


class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'vendor', 'discount']  # Исправлено здесь
    search_fields = ['code', 'vendor__username']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total', 'payment_status', 'order_status', 'payment_method', 'date']  # Исправлено здесь
    list_editable = ['payment_status', 'order_status', 'payment_method']  # Поля должны соответствовать list_display
    search_fields = ['id', 'customer__username']  # Исправлено здесь
    list_filter = ['payment_status', 'order_status']


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'qty', 'price', 'total']  # Исправлено здесь
    search_fields = ['id', 'order__order_id', 'product__name']
    list_filter = ['order__date']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'active', 'date']  # Исправлено здесь
    search_fields = ['user__username', 'product__name']
    list_filter = ['active', 'rating']


admin.site.register(store_model.Category, CategoryAdmin)
admin.site.register(store_model.Product, ProductAdmin)
admin.site.register(store_model.Variant, VariantAdmin)
admin.site.register(store_model.VariantItem, VariantItemAdmin)
admin.site.register(store_model.Gallery, GalleryAdmin)  # Исправлено здесь
admin.site.register(store_model.Cart, CartAdmin)
admin.site.register(store_model.Coupon, CouponAdmin)
admin.site.register(store_model.Order, OrderAdmin)
admin.site.register(store_model.OrderItem, OrderItemAdmin)
admin.site.register(store_model.Review, ReviewAdmin)
