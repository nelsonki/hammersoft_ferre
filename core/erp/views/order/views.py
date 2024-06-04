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

from core.erp.forms import ClientForm, OutputForm
from core.erp.mixins import Configuration, ValidatePermissionRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, TemplateView

from core.erp.models import Client, DetProdCombo, Output, ProdCombo, Product, DetOutput, Inventory, StoreProdStock, Order, DetOrder
from django.template.loader import get_template

from xhtml2pdf import pisa

from core.erp.forms import OutputForm, OrderForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from django.db.models import Q

from datetime import datetime
from django.db.models import Sum

class OrderListView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Order
    template_name = 'order/list.html'
    permission_required = 'view_order'
    url_redirect= reverse_lazy('dashboard')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Order.objects.all().filter(Q(is_active=1)):
                    data.append(i.toJSON())
            elif action == 'search_details_prod':
                data = []
                for i in DetOrder.objects.filter(order_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ordenes de Salidas'
        context['create_url'] = reverse_lazy('order_create')
        context['list_url'] = reverse_lazy('order_list')
        context['entity'] = 'Ordenes de Salida'
        return context


class OrderCreateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'order/create.html'
    success_url = reverse_lazy('order_list')
    permission_required = 'add_order'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        #prods = Product.objects.filter(name__icontains=request.POST['term'])[0:10]
        data = {}
        try:
            action = request.POST['action']                       
            if action == 'search_products':
                data = [] 
                storeViene =request.POST['vaStore']
                print(storeViene)
                if storeViene:               
                    ids_exclude = json.loads(request.POST['ids'])
                    term = request.POST['term'].strip()
                    products = Product.objects.filter(Q(stock__gt=0) | (Q(is_combo=1) & Q(pvp__gt=0)))
                    if len(term):
                        products = products.filter(name__icontains=term)
                    for i in products.filter(store__in=storeViene).exclude(id__in=ids_exclude)[0:10]:
                        storeProdStock = StoreProdStock.objects.get(store__in=[storeViene], prod__in=[i.id])
                        item = i.toJSON()
                        item['value'] = i.name
                        item['stock'] = storeProdStock.stock_in

                        # item['text'] = i.name
                        data.append(item)
            elif action == 'add':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    order = Order()
                    order.date_joined = vents['date_joined'] 
                    order.cli_id = vents['cli']
                    order.store_id = vents['store']
                    order.subtotal = float(vents['subtotal'])
                    order.tax = float(vents['tax'])
                    order.total = float(vents['total'])
                    order.peso = float(vents['pesos'])
                    order.bolivar = float(vents['bolivares'])
                    order.save()
                    for i in vents['products']:
                        det = DetOrder()
                        det.order_id = order.id
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])
                        det.save()
                    data = {'id': order.id}
            elif action == 'search_clients':
                data = []
                term = request.POST['term']
                clients = Client.objects.filter(
                    Q(name__icontains=term) | Q(lastname__icontains=term) | Q(dni__icontains=term))[0:10]
                for i in clients:
                    item = i.toJSON()
                    item['text'] = i.get_full_name()
                    data.append(item)
            elif action == 'create_client':
                with transaction.atomic():
                    frmClient = ClientForm(request.POST)
                    data = frmClient.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de una Orden de Salida'
        context['entity'] = 'Ordenes de Salida'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['frmClient'] = ClientForm()
        context['det'] = []
        return context


class OrderUpdateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'order/create.html'
    success_url = reverse_lazy('order_list')
    permission_required = 'change_order'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None ):
        instance = self.get_object()
        form = OrderForm(instance=instance)
        form.fields['cli'].queryset = Client.objects.filter(id=instance.cli.id)
        return form
    
    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                ids_exclude = json.loads(request.POST['ids'])
                term = request.POST['term'].strip()
                products = Product.objects.filter(Q(stock__gt=0) | (Q(is_combo=1) & Q(pvp__gt=0)))
                if len(term):
                    products = products.filter(name__icontains=term)
                for i in products.exclude(id__in=ids_exclude)[0:10]:
                    item = i.toJSON()
                    item['value'] = i.name
                    # item['text'] = i.name
                    data.append(item)
                    
            elif action == 'edit':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    output = Output()
                    output.date_joined = vents['date_joined'] 
                    output.cli_id = vents['cli']
                    output.store_id = vents['store']
                    output.subtotal = float(vents['subtotal'])
                    output.tax = float(vents['tax'])
                    output.total = float(vents['total'])
                    output.peso = float(vents['pesos'])
                    output.bolivar = float(vents['bolivares'])
                    output.save()
                    order = Order.objects.get(id=self.get_object().id)#cambiar este numero por el id de la orden
                    order.is_active='0'
                    order.save()
                    for i in vents['products']:
                        det = DetOutput()
                        inve = Inventory() 
                        storeProdStock = StoreProdStock()
                        det.output_id = output.id
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])
                        inve.prod_id = i['id']
                        inve.in_store_id = vents['store']
                        inve.out_store_id = vents['store']
                        inve.stock = int(i['amount'])
                        inve.types = 2
                        inve.operaOut_id = output.id
                        inve.save()
                        det.save()
                        
                        if  Product.objects.filter(Q(id=i['id']) & Q(is_combo=1)):
                            prodcombo = ProdCombo.objects.filter(prod_id=i['id'])
                            for p in prodcombo:
                                item = p.toJSON()
                                for j in DetProdCombo.objects.filter(prodcombo_id=item['id']):
                                    itemj = j.toJSON()
                                    print(itemj['prod']['id'])
                                    storeProdStock = StoreProdStock.objects.get(store__in=[vents['store']], prod__in=[itemj['prod']['id']])
                                    storeProdStock.stock_in -= (itemj['amount'] * det.amount)
                                    storeProdStock.save()
                        else:                              
                            storeProdStock = StoreProdStock.objects.get(store__in=[vents['store']], prod__in=[i['id']])
                            storeProdStock.stock_in -= det.amount
                            storeProdStock.save()
                            print('otro producto')                 
                    data = {'id': output.id}                      
            elif action == 'search_clients':
                data = []
                term = request.POST['term']
                clients = Client.objects.filter(
                    Q(name__icontains=term) | Q(lastname__icontains=term) | Q(dni__icontains=term))[0:10]
                for i in clients:
                    item = i.toJSON()
                    item['text'] = i.get_full_name()
                    data.append(item)
            elif action == 'create_client':
                with transaction.atomic():
                    frmClient = ClientForm(request.POST)
                    data = frmClient.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_details_product(self):
        data=[]
        try:
           for i in DetOrder.objects.filter(order_id=self.get_object().id):
               item = i.prod.toJSON()
               item['amount'] =i.amount
               data.append(item)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar una Orden de Salida'
        context['entity'] = 'Ordenes de Salida'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['frmClient'] = ClientForm()
        context['det'] = json.dumps(self.get_details_product())
        return context
 

class OrderDeleteView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Order
    template_name = 'order/delete.html'
    success_url = reverse_lazy('order_list')
    permission_required = 'delete_order'
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
        context['title'] = 'Eliminación de una Orden de Salida'
        context['entity'] = 'Ordenes de salida'
        context['list_url'] = self.success_url
        return context

