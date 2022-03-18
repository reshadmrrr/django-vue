import traceback
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, View, TemplateView
import json
from django.core import serializers

from product.models import Product, ProductVariant, ProductVariantPrice, Variant
from product.serializers import ProductSerializer, ProductVariantSerializer, ProductVariantPriceSerializer
    
class ProductView(ListView):
    paginate_by = 2
    model = Product
    template_name = 'products/list.html'
    
    def get_queryset(self):
        filter_string = {}
        if self.request.GET.get('title', ''): 
            filter_string['title__icontains'] = self.request.GET.get('title')
        if self.request.GET.get('variant', ''): 
            filter_string['product_variants__variant_title'] = self.request.GET.get('variant', '')
        price_from = self.request.GET.get('price_from', '')
        price_to = self.request.GET.get('price_to', '')
        product_variant_prices_qs = ProductVariantPrice.objects.all()
        if price_from or price_to:
            if price_from and price_to: 
                # filter_string['product_variant_prices__price__range'] = [price_from, price_to]
                product_variant_prices_qs = product_variant_prices_qs.filter(price__range = [price_from, price_to])
            elif price_from: 
                # filter_string['product_variant_prices__price__gte'] = price_from
                product_variant_prices_qs = product_variant_prices_qs.filter(price__gte = price_from)
            elif price_to: 
                # filter_string['product_variant_prices__price__lte'] = price_to
                product_variant_prices_qs = product_variant_prices_qs.filter(price__lte = price_to)
        filter_string['product_variant_prices__in'] = product_variant_prices_qs
        if self.request.GET.get('date', ''):
            filter_string['updated_at__contains'] = self.request.GET.get('date', '')
        return Product.objects.prefetch_related('product_variants', 'product_variant_prices').filter(**filter_string).order_by("id").distinct() if filter_string else Product.objects.all().order_by("id")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = True
        context['variants'] = Variant.objects.prefetch_related("variant_variants").filter(active=True)
        for key in self.request.GET:
            if len(self.request.GET.get(key)):
                context[f'filter_{key}'] = self.request.GET.get(key)
        return context
    
    
class CreateProductView(TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        # print(data)
        # return JsonResponse({"data": 1})
        
        product = Product(title=data['title'], sku=data['sku'], description=data['description'])
        product.save()
        tags = {}
        for item in data['product_variant']:
            variant = Variant.objects.get(id=item['option'])
            for tag in item['tags']:
                product_variant = ProductVariant(variant_title=tag, variant=variant, product=product)
                product_variant.save()
                tags[tag] = product_variant
        # product_variants = tags.values()
        # print(product_variants)
        # ProductVariant.objects.bulk_create(product_variants)
        product_variant_prices = []
        for item in data['product_variant_prices']:
            product_variants = [None] * 3
            splitted = item['title'].split('/')
            for i in range(len(splitted)):
                if splitted[i]: product_variants[i] = splitted[i]
            product_variant_prices.append(ProductVariantPrice(product_variant_one=tags.get(product_variants[0], None), product_variant_two=tags.get(product_variants[1], None), product_variant_three=tags.get(product_variants[2], None), price=item['price'], stock=item['stock'], product=product))      
        ProductVariantPrice.objects.bulk_create(product_variant_prices)
        return JsonResponse({"data": 1})
    
    
def edit_product(request, id):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            id = data['id']
            product = Product.objects.get(id=id)
            product.title = data['title']           
            product.sku = data['sku']           
            product.description = data['description']
            product.save()
            ProductVariant.objects.filter(product=product).delete()
            tags = {}
            for item in data['product_variant']:
                variant = Variant.objects.get(id=item['option'])
                for tag in item['tags']:
                    product_variant = ProductVariant(variant_title=tag, variant=variant, product=product)
                    product_variant.save()
                    tags[tag] = product_variant
            product_variant_prices = []
            for item in data['product_variant_prices']:
                product_variants = [None] * 3
                splitted = item['title'].split('/')
                for i in range(len(splitted)):
                    if splitted[i]: product_variants[i] = splitted[i]
                product_variant_prices.append(ProductVariantPrice(product_variant_one=tags.get(product_variants[0], None), product_variant_two=tags.get(product_variants[1], None), product_variant_three=tags.get(product_variants[2], None), price=item['price'], stock=item['stock'], product=product))      
            ProductVariantPrice.objects.bulk_create(product_variant_prices)         
            return JsonResponse({"data": 1})
        else:       
            product = Product.objects.prefetch_related('product_variants', 'product_variant_prices', 'product_variant_prices').get(id=id)
            variants = Variant.objects.filter(active=True).values('id', 'title')
            context = {
                'product': json.dumps(ProductSerializer(product).data),
                'product_variants': json.dumps(ProductVariantSerializer(product.product_variants.all(), many=True).data),
                'product_variant_prices': json.dumps(ProductVariantPriceSerializer(product.product_variant_prices.all(), many=True).data),
                'variants': list(variants),
                'update': True                
            }
            return render(request, 'products/create.html', context)
            # return render(request, 'products/edit.html', context)
    except:
        print(traceback.format_exc())
        return redirect('dashboard')

