from django.views.generic import ListView, View, TemplateView

from product.models import Product, ProductVariant, Variant
    
class ProductView(ListView):
    template_name = 'products/list.html'
    paginate_by = 2
    
    def get_queryset(self):
        filter_string = {}
        print(self.request.GET)
        for key in self.request.GET:
            if self.request.GET.get(key):
                filter_string[key] = self.request.GET.get(key) 
        return Product.objects.filter(**filter_string)   
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = True
        context['product_variants'] = ProductVariant.objects.filter(variant__active=True).select_related("variant")
        return context
    
    
class CreateProductView(TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
