from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<slug>/', views.product_detail, name='product-detail'), # <slug> come from views.py
]
