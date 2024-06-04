from typing import Any
from django.db.models import Sum
 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.db.models import Q

from core.erp.mixins import Configuration, IsSuperUserMixin, ValidatePermissionRequiredMixin
from core.erp.models import  DetOutput, DetProdCombo, ProdCombo, Product, StoreProdStock
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from core.erp.forms import ProductForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from core.erp.mixins import ValidatePermissionRequiredMixin


class ProductListView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model=Product
    template_name = 'product/list.html'
    permission_required = 'view_product'
    url_redirect= reverse_lazy('dashboard')

    @method_decorator(csrf_exempt)
    #@method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    #sobre escribir el metodo post
    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Product.objects.filter(Q(cate__isnull=False) | Q(cate__name__isnull=False)):
                    item = i.toJSON()
                    item['stock_general'] = StoreProdStock.objects.filter(prod_id=i.id).aggregate(stock_in=Sum('stock_in')).get('stock_in') or 0 
                    data.append(item)
            elif action == 'search_details_prod_combo':
                for i in ProdCombo.objects.filter(prod_id=request.POST['id']):
                    data = []                        
                    for j in DetProdCombo.objects.filter(prodcombo_id=i.id):
                        data.append(j.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Producto'
        context['create_url'] = reverse_lazy('product_create')
        context['list_url'] = reverse_lazy('product_list')
        context['entity'] = 'Lista de Productos'

        return context


class ProductCreateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/create.html'
    success_url = reverse_lazy('product_list')
    permission_required = 'product.add_product'
    url_redirect = success_url

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)
    

    '''def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url)
        self.object =None
        context = self.get_context_data(**kwargs)
        context['form']=form
        return  render(request, self.template_name, context)'''
 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Producto'
        context['list_url'] = reverse_lazy('product_list')
        context['entity'] = 'Productos'
        context['action'] = 'add'
        return context


class ProductUpdateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/create.html'
    success_url = reverse_lazy('product_list')
    permission_required = 'change_product'
    url_redirect = success_url

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)
    
    def product_stock_general(self):
        product_stock_general = StoreProdStock.objects.filter(prod_id=self.object.id).aggregate(stock_in=Sum('stock_in')).get('stock_in') or 0 
        print(product_stock_general)
        return product_stock_general
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Producto'
        context['entity'] = 'Productos'
        context['product_stock_general'] = self.product_stock_general()
        context['list_url'] = reverse_lazy('product_list')
        context['action'] = 'edit'
        return context


class ProductDeleteView(Configuration, LoginRequiredMixin, IsSuperUserMixin, ValidatePermissionRequiredMixin,  DeleteView):
    model = Product
    template_name = 'product/delete.html'
    success_url = reverse_lazy('product_list')
    permission_required = 'delete_product'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar un Producto'
        context['entity'] = 'Productos'
        context['list_url'] = reverse_lazy('product_list')
        return context



