from django.views.generic import ListView, View, TemplateView
from django.db.models import Q

from product.models import Product, ProductVariant, ProductVariantPrice, Variant
    
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
