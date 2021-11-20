# Django
from django.urls import path
# Core
from core.views import HomeView, remove_one_product_from_sale, add_one_product_to_sale, finish_sale

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('remove_one_product_from_sale/<pk>/', remove_one_product_from_sale, name='remove_one_product_from_sale'),
    path('add_one_product_to_sale/<pk>/', add_one_product_to_sale, name='add_one_product_to_sale'),
    path('finish_sale/<pk>/', finish_sale, name='finish_sale'),
]