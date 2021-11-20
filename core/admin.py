from django.contrib import admin
from core.models import Category, Brand, Product, SellingPrice, Lot, SaleProduct, Sale

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'description', 'presentation', 'barcode', 'stock', 'investment']

@admin.register(SellingPrice)
class SellingPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'unit_price']

@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'unit_purchase_price', 'package_purchase_price', 'units_per_package', 'created_at']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'income', 'gross_profit', 'sold', 'sold_at']