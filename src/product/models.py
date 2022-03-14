from django.db import models
from config.g_model import TimeStampMixin
import random
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify


# Create your models here.
class Variant(TimeStampMixin):
    title = models.CharField(max_length=40, unique=True)
    description = models.TextField()
    active = models.BooleanField(default=True)


class Product(TimeStampMixin):
    title = models.CharField(max_length=255)
    sku = models.SlugField(max_length=255, unique=True)
    description = models.TextField()


class ProductImage(TimeStampMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file_path = models.URLField()


class ProductVariant(TimeStampMixin):
    variant_title = models.CharField(max_length=255)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='variant_variants')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variants')


class ProductVariantPrice(TimeStampMixin):
    product_variant_one = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True,
                                            related_name='product_variant_one')
    product_variant_two = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True,
                                            related_name='product_variant_two')
    product_variant_three = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True,
                                              related_name='product_variant_three')
    price = models.FloatField()
    stock = models.FloatField()
    product = models.ForeignKey(Product, related_name="product_variant_prices", on_delete=models.CASCADE)
    
    
def slugify_sku(sku):
    if len(sku) >= 50:
        sku_slug = slugify(sku[:50])
    else:
        sku_slug = slugify(sku)
    return (
        sku_slug + "-" + "".join(random.choice("0123456789abcdef") for i in range(9))
    )


@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, *args, **kwargs):
    instance.sku = slugify_sku(instance.sku)