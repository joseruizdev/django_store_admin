# Django
from django.db import models
from django.utils.translation import gettext_lazy

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=gettext_lazy('name'))

    class Meta:
        verbose_name = gettext_lazy('category')
        verbose_name_plural = gettext_lazy('categories')

    def __str__(self) -> str:
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name=gettext_lazy('name'))

    class Meta:
        verbose_name = gettext_lazy('brand')
        verbose_name_plural = gettext_lazy('brands')

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=gettext_lazy('category'))
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name=gettext_lazy('brand'))
    description = models.CharField(max_length=255, verbose_name=gettext_lazy('description'))
    presentation = models.CharField(max_length=255, verbose_name=gettext_lazy('presentation'))
    barcode = models.CharField(max_length=128, verbose_name=gettext_lazy('barcode'))

    @property
    def name(self):
        return f'{self.category.name} {self.brand.name} {self.description} {self.presentation}'