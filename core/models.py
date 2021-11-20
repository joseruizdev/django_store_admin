# Python
from decimal import Decimal
from django.contrib.messages.api import warning
# Django
from django.db import models
from django.utils.translation import gettext_lazy
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib import messages
from django.shortcuts import redirect

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=gettext_lazy("name"))

    class Meta:
        verbose_name = gettext_lazy("category")
        verbose_name_plural = gettext_lazy("categories")

    def __str__(self) -> str:
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name=gettext_lazy("name"))

    class Meta:
        verbose_name = gettext_lazy("brand")
        verbose_name_plural = gettext_lazy("brands")

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=gettext_lazy("category"))
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name=gettext_lazy("brand"))
    description = models.CharField(max_length=255, verbose_name=gettext_lazy("description"))
    presentation = models.CharField(max_length=255, verbose_name=gettext_lazy("presentation"))
    barcode = models.CharField(max_length=128, verbose_name=gettext_lazy("barcode"))

    @property
    def name(self):
        return f"{self.category.name} {self.brand.name} {self.description} {self.presentation}"

    @property
    def stock(self):
        try:
            lots = Lot.objects.filter(product=self).all()
            stock = 0
            for lot in lots:
                stock += lot.quantity
        except Lot.DoesNotExist:
            stock = 0
        return stock

    @property
    def investment(self):
        lots = Lot.objects.filter(product=self).all()
        amount_invested = 0
        for lot in lots:
            amount_invested_per_lot = lot.quantity * lot.unit_purchase_price
            amount_invested += amount_invested_per_lot
        return amount_invested

    def __str__(self) -> str:
        return self.name


class SellingPrice(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name=gettext_lazy("product"))
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=gettext_lazy("unit price"))

    class Meta:
        verbose_name = gettext_lazy("selling price")
        verbose_name_plural = gettext_lazy("selling prices")

    def __str__(self):
        return f"Selling price of {self.product.name}"


class Lot(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=gettext_lazy("product"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=gettext_lazy("quantity"))
    unit_purchase_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=gettext_lazy("unit purchase price"))
    package_purchase_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=gettext_lazy("package purchase price"))
    units_per_package = models.PositiveIntegerField(default=1, verbose_name=gettext_lazy("units per package"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=gettext_lazy("created at"))

    class Meta:
        verbose_name = gettext_lazy("lot")
        verbose_name_plural = gettext_lazy("lots")
        get_latest_by = "created_at"

    def __str__(self):
        return f"Lot of {self.product.name} registered at {self.created_at}"


class SaleProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=gettext_lazy("product"))
    unit_purchase_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name=gettext_lazy("unit purchase price"))
    unit_selling_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name=gettext_lazy("unit selling price"))
    sold = models.BooleanField(default=False, verbose_name=gettext_lazy("sold"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=gettext_lazy("quantity"))

    @property
    def accumulated_purchase_price(self):
        accumulated_purchase_price = self.quantity * self.unit_purchase_price

    @property
    def accumulated_price(self):
        accumulated_price = self.quantity * self.unit_selling_price
        return accumulated_price

    class Meta:        
        verbose_name = gettext_lazy("sale product")
        verbose_name_plural = gettext_lazy("sale products")

    def __str__(self):
        return f"Product: {self.product.name} Quantity: {self.quantity}" 


class Sale(models.Model):
    products = models.ManyToManyField(SaleProduct, verbose_name=gettext_lazy("products"))
    sold = models.BooleanField(default=False, verbose_name=gettext_lazy("sold"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=gettext_lazy("created at"))
    sold_at = models.DateTimeField(null=True, verbose_name=gettext_lazy("sold at"))
    income = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name=gettext_lazy("income"))
    gross_profit = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name=gettext_lazy("gross profit"))

    @property
    def total_price(self):
        total_price = Decimal(0.0)
        for sale_product in self.products.all():
            total_price += sale_product.accumulated_price
        return total_price

    class Meta:
        verbose_name = gettext_lazy("sale")
        verbose_name_plural = gettext_lazy("sales")

    def __str__(self):
        return f"{self.created_at}"


class Scan(models.Model):
    barcode = models.CharField(max_length=128, verbose_name=gettext_lazy("barcode"))

    class Meta:
        verbose_name = gettext_lazy("scan")
        verbose_name_plural = gettext_lazy("scans")

    def __str__(self):
        return self.barcode

# TODO: Replace console prints with messages or something else

@receiver(post_save, sender=Scan)
def create_sale(instance, **kwargs):
    scan = instance
    barcode = scan.barcode

    if Product.objects.filter(barcode=barcode).exists():
        product = Product.objects.filter(barcode=barcode).get()
        if Lot.objects.filter(product=product).exists():
            earliest_lot = Lot.objects.filter(product=product).earliest()
            lots_of_product = Lot.objects.filter(product=product).all()
            product_stock = 0
            for lot in lots_of_product:
                product_stock += lot.quantity
            if SellingPrice.objects.filter(product=product).exists():

                if product_stock >= 0:
                    if Sale.objects.filter(sold=False).exists():
                        sale = Sale.objects.filter(sold=False).get()
                        if SaleProduct.objects.filter(product=product, sold=False).exists():
                            sale_product = SaleProduct.objects.filter(product__barcode=product.barcode, sold=False).get()
                            if sale_product.quantity >= product_stock:
                                print("There are no products in stock.")
                            else:
                                sale_product.quantity += 1
                                sale_product.save()
                                print("The product quantity has been updated!")
                        else:
                            if SellingPrice.objects.filter(product=product).exists():
                                selling_price = SellingPrice.objects.filter(product=product).get()
                                sale_product = SaleProduct.objects.create(
                                    product=product,
                                    unit_purchase_price=earliest_lot.unit_purchase_price,
                                    unit_selling_price=selling_price.unit_price
                                )
                                sale.products.add(sale_product)
                                print("Product added!")
                            else:
                                print("The product does not have a selling price.")
                    else:
                        if SellingPrice.objects.filter(product=product).exists():
                            selling_price = SellingPrice.objects.filter(product=product).get()
                            sale_product = SaleProduct.objects.create(
                                product=product,
                                unit_purchase_price=earliest_lot.unit_purchase_price,
                                unit_selling_price=selling_price.unit_price
                            )
                            sale = Sale.objects.create()
                            sale.products.add(sale_product)
                            print("Product added!")
                        else:
                            print("The product does not have a selling price.")
                else:
                    print("This product is out of stock.")
                
            else:
                print("The product does not have a selling price.")
        else:
            print("This product is out of stock.")
    else:
        print("This product doesn't exist.")