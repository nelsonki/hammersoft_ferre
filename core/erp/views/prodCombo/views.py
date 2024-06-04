import json
import os
from django.conf import settings

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms.models import BaseModelForm

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.erp.forms import ClientForm, OutputForm, ProComboForm
from core.erp.mixins import Configuration, ValidatePermissionRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, TemplateView

from core.erp.models import Client, DetProdCombo, Output, ProdCombo, Product, DetOutput, Inventory, StoreProdStock
from django.template.loader import get_template

from xhtml2pdf import pisa

from core.erp.forms import OutputForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from django.db.models import Q
 
from datetime import datetime
from django.db.models import Sum

class ProdComboListView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = ProdCombo
    template_name = 'prodCombo/list.html'
    permission_required = 'view_prodcombo'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in ProdCombo.objects.all():
                    data.append(i.toJSON())
            elif action == 'search_details_prod':
                data = []
                for i in DetProdCombo.objects.filter(prodcombo_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Combos'
        context['create_url'] = reverse_lazy('prodcombo_create')
        context['list_url'] = reverse_lazy('prodcombo_list')
        context['entity'] = 'Combos'
        return context


class ProdComboCreateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = ProdCombo
    form_class = ProComboForm
    template_name = 'prodCombo/create.html'
    success_url = reverse_lazy('prodcombo_list')
    permission_required = 'add_prodcombo'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        #prods = Product.objects.filter(name__icontains=request.POST['term'])[0:10]
        data = {}
        try:
            action = request.POST['action']  
            print(action)         
            if action == 'search_products2':
                data = [] 
                storeViene =request.POST['vaStore']
                if storeViene:              
                    ids_exclude = json.loads(request.POST['ids'])
                    term = request.POST['term'].strip()
                    #products = Product.objects.filter(stock__gt=0)
                    if len(term):
                        products = Product.objects.filter(name__icontains=term)
                    for i in products.filter(store__in=storeViene).exclude(is_combo=0)[0:10]:
                        storeProdStock = StoreProdStock.objects.get(store__in=[storeViene], prod__in=[i.id])
                        item = i.toJSON()
                        item['text'] = i.name
                        data.append(item)
            elif action == 'search_products':
                data = [] 
                storeViene =request.POST['vaStore']
                print(storeViene)
                if storeViene:              
                    ids_exclude = json.loads(request.POST['ids'])
                    term = request.POST['term'].strip()
                    products = Product.objects.filter(stock__gt=0)
                    if len(term):
                        products = products.filter(name__icontains=term)
                    for i in products.filter(store__in=storeViene).exclude(id__in=ids_exclude)[0:10]:
                        storeProdStock = StoreProdStock.objects.get(store__in=[storeViene], prod__in=[i.id])
                        item = i.toJSON()
                        item['value'] = i.name #con esta opcion podemos enviar y dibujar un buen template para mostrar la informacion completa
                        item['stock'] = storeProdStock.stock_in
                        # item['text'] = i.name con esta opcion enviamos solo el nombre al combo
                        data.append(item)
            elif action == 'add':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    prodcombo = ProdCombo()
                    prodcombo.store_id = vents['store']
                    prodcombo.prod_id = vents['prod']
                    prodcombo.name = vents['name']
                    prodcombo.subtotal = float(vents['subtotal'])
                    prodcombo.save()
                    product = Product.objects.get(id=prodcombo.prod_id)
                    product.pvp = prodcombo.subtotal
                    product.pvp2 = prodcombo.subtotal
                    product.pvp3 = prodcombo.subtotal
                    product.save()
                    for i in vents['products']:
                        det = DetProdCombo()
                        det.prodcombo_id = prodcombo.id
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])
                        det.save()
                    data = {'id': prodcombo.id}
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de un Combo'
        context['entity'] = 'Combos'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['det'] = []
        return context


class ProdComboUpdateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = ProdCombo
    form_class = ProComboForm
    template_name = 'prodcombo/create.html'
    success_url = reverse_lazy('prodcombo_list')
    permission_required = 'change_prodcombo'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None ):
        instance = self.get_object()
        form = ProComboForm(instance=instance)
        form.fields['prod'].queryset = Product.objects.filter(id=instance.prod.id)
        return form
    
    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products2':
                data = [] 
                storeViene =request.POST['vaStore']
                if storeViene:              
                    ids_exclude = json.loads(request.POST['ids'])
                    term = request.POST['term'].strip()
                    #products = Product.objects.filter(stock__gt=0)
                    if len(term):
                        products = Product.objects.filter(name__icontains=term)
                    for i in products.filter(store__in=storeViene).exclude(is_combo=0)[0:10]:
                        storeProdStock = StoreProdStock.objects.get(store__in=[storeViene], prod__in=[i.id])
                        item = i.toJSON()
                        item['text'] = i.name
                        data.append(item)
            elif action == 'search_products':
                data = [] 
                storeViene =request.POST['vaStore']
                print(storeViene)
                if storeViene:              
                    ids_exclude = json.loads(request.POST['ids'])
                    term = request.POST['term'].strip()
                    products = Product.objects.filter(stock__gt=0)
                    if len(term):
                        products = products.filter(name__icontains=term)
                    for i in products.filter(store__in=storeViene).exclude(id__in=ids_exclude)[0:10]:
                        storeProdStock = StoreProdStock.objects.get(store__in=[storeViene], prod__in=[i.id])
                        item = i.toJSON()
                        item['value'] = i.name #con esta opcion podemos enviar y dibujar un buen template para mostrar la informacion completa
                        item['stock'] = storeProdStock.stock_in
                        # item['text'] = i.name con esta opcion enviamos solo el nombre al combo
                        data.append(item)
            elif action == 'edit':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    prodcombo = self.get_object()
                    prodcombo.store_id = vents['store']
                    prodcombo.prod_id = vents['prod']
                    prodcombo.name = vents['name']
                    prodcombo.subtotal = float(vents['subtotal'])
                    prodcombo.save()
                    product = Product.objects.get(id=prodcombo.prod_id)
                    product.pvp = prodcombo.subtotal
                    product.pvp2 = prodcombo.subtotal
                    product.pvp3 = prodcombo.subtotal
                    product.save()
                    prodcombo.detprodcombo_set.all().delete()
                    for i in vents['products']:
                        det = DetProdCombo()
                        det.prodcombo_id = prodcombo.id
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])
                        det.save()
                    data = {'id': prodcombo.id}
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_details_product(self):
        data=[]
        try:
           for i in DetProdCombo.objects.filter(prodcombo_id=self.get_object().id):
               item = i.prod.toJSON()
               item['amount'] =i.amount
               data.append(item)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar un Combo'
        context['entity'] = 'Combos'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['det'] = json.dumps(self.get_details_product())
        return context
 

class ProdComboDeleteView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = ProdCombo
    template_name = 'prodCombo/delete.html'
    success_url = reverse_lazy('prodcombo_list')
    permission_required = 'delete_prodcombo'
    url_redirect = reverse_lazy('dashboard')
    
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
        context['title'] = 'Eliminación de un Combo'
        context['entity'] = 'Combos'
        context['list_url'] = self.success_url
        return context

 