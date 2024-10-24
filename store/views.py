from django.shortcuts import render, redirect
from store import models as store_models


def index(request):
    products = store_models.Product.objects.filter(status='Published')

    context = {
        'products': products,
    }

    return render(request, 'store/index.html', context)


def product_detail(request, slug):
    product = store_models.Product.objects.get(status='Published', slug=slug) # 1st slug come from models.py
    related_products = store_models.Product.objects.filter(category=product.category, status='Published').exclude(id=product.id)
    product_stock_range = range(1, product.stock + 1)

    context = {
        'product': product,
        'related_products': related_products,
        'product_stock_range': product_stock_range,
    }

    return render(request, 'store/product-detail.html', context)