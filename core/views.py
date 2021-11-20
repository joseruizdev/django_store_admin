# Python
from decimal import Decimal
# Django
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Core
from core.models import Category, Brand, Product, SellingPrice, Lot, SaleProduct, Sale, Scan
from core.forms import BarcodeForm

# Create your views here.

class HomeView(TemplateView):
    def get(self, *args, **kwargs):
        form = BarcodeForm()
        try:
            sale = Sale.objects.filter(sold=False).get()
            context = {
                'form': form,
                'sale': sale,
            }
        except Sale.DoesNotExist:
            # messages.error(self.request, "No hay una venta activa!")
            context = {
                'form': form,
            }
        return render(self.request, 'home.html', context)

    def post(self, request, *args, **kwargs):
        form = BarcodeForm(request.POST)
        if form.is_valid():
            barcode = form.cleaned_data.get('barcode')
            scan = Scan.objects.create(barcode=barcode)
        # HttpResponseRedirect clear POST data.
        return HttpResponseRedirect(request.path)

@login_required
def add_one_product_to_sale(request, pk):
    product = Product.objects.filter(pk=pk).get()
    if Sale.objects.filter(sold=False).exists():
        sale = Sale.objects.filter(sold=False).get()
        try:
            sale_product = SaleProduct.objects.get(product=product, sold=False)
            lots_of_product = Lot.objects.filter(product=product).all()
            product_stock = 0
            for lot in lots_of_product:
                product_stock += lot.quantity
                
            if sale_product.quantity >= product_stock:
                messages.warning(request, "Ya no quedan productos en stock, no puede agregar mas.")
            else:
                sale_product.quantity += 1
                sale_product.save()
                messages.info(request, "La cantidad de producto se modifico exitosamente!")
            return redirect("core:home")
        except SaleProduct.DoesNotExist:
            messages.info(request, "Este producto no estaba en la venta!")
            return redirect("core:home")
    else:
        return redirect("core:home")

@login_required
def remove_one_product_from_sale(request, pk):
    product = Product.objects.filter(pk=pk).get()
    if Sale.objects.filter(sold=False).exists():
        sale = Sale.objects.filter(sold=False).get()
        try:
            sale_product = SaleProduct.objects.get(product=product, sold=False)
            if sale_product.quantity <= 1:
                sale_product.delete()
                if sale.products.exists() == False:
                    sale.delete()
                messages.info(request, "Venta eliminada.")
            else:
                sale_product.quantity -= 1
                sale_product.save()
                messages.info(request, "La cantidad de producto se modifico exitosamente!")
            return redirect("core:home")
        except SaleProduct.DoesNotExist:
            messages.danger(request, "Este producto no estaba en la venta!")
            return redirect("core:home")
    else:
        return redirect("core:home")

@login_required
def finish_sale(request, pk):
    sale = Sale.objects.get(pk=pk)
    total_cost = Decimal(0.0)
    total_price = Decimal(0.0)
    for sale_product in sale.products.all():
        product = sale_product.product
        earliest_lot = Lot.objects.filter(product=product).earliest()
        if earliest_lot.quantity == sale_product.quantity:
            earliest_lot.delete()
        else:
            if earliest_lot.quantity >= sale_product.quantity:
                earliest_lot.quantity -= sale_product.quantity
                earliest_lot.save()
            else:
                missing_products = sale_product.quantity - earliest_lot.quantity
                next_lot = Lot.objects.filter(product=product).order_by('created_at')[1]
                next_lot.quantity -= missing_products
                next_lot.save()
                earliest_lot.delete()
        accumulated_purchase_price = sale_product.quantity * sale_product.unit_purchase_price
        total_cost += accumulated_purchase_price
        accumulated_selling_price = sale_product.quantity * sale_product.unit_selling_price
        total_price += accumulated_selling_price
        sale_product.sold = True
        sale_product.save()
    sale.sold = True
    sale.sold_at = timezone.now()
    sale.income = total_price
    sale.gross_profit = sale.total_price - total_cost
    sale.save()
    scans = Scan.objects.all()
    scans.delete()
    messages.success(request, 'Venta finalizada!')
    return redirect("core:home")