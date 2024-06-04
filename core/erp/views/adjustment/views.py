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

from core.erp.forms import ClientForm, AdjustmentForm
from core.erp.mixins import Configuration, ValidatePermissionRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, TemplateView

from core.erp.models import Client, DetProdCombo, Adjustment, ProdCombo, Product, DetAdjustment, Inventory, StoreProdStock
from django.template.loader import get_template

from xhtml2pdf import pisa

from core.erp.forms import AdjustmentForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from django.db.models import Q

from datetime import datetime
from django.db.models import Sum

class AdjustmentListView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Adjustment
    template_name = 'adjustment/list.html'
    permission_required = 'view_adjustment'
    url_redirect = reverse_lazy('dashboard')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Adjustment.objects.all():
                    data.append(i.toJSON())
            elif action == 'search_details_prod':
                data = []
                for i in DetAdjustment.objects.filter(adjustment_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ajustes'
        context['create_url'] = reverse_lazy('adjustment_create')
        context['list_url'] = reverse_lazy('adjustment_list')
        context['entity'] = 'Adjustes'
        return context


class AdjustmentCreateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Adjustment
    form_class = AdjustmentForm
    template_name = 'adjustment/create.html'
    success_url = reverse_lazy('adjustment_list')
    permission_required = 'add_adjustment'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        #prods = Product.objects.filter(name__icontains=request.POST['term'])[0:10]
        data = {}
        try:
            action = request.POST.get('action', '')
            if action == 'search_products':                 
                data = [] 
                storeViene =request.POST['vaStore']
                if storeViene:                                
                    ids_exclude = json.loads(request.POST['ids'])
                    term = request.POST['term'].strip()                    
                    products = Product.objects.filter().exclude(is_combo=1)
                    if len(term):
                        products = products.filter(name__icontains=term)
                    for i in products.filter(store__in=storeViene).exclude(id__in=ids_exclude)[0:10]:                        
                        storeProdStock = StoreProdStock.objects.get(store__in=[storeViene], prod__in=[i.id])                         
                        item = i.toJSON()
                        item['value'] = i.name
                        item['stock'] = storeProdStock.stock_in
                        data.append(item)      
            elif action == 'add':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    adjustment = Adjustment()
                    adjustment.date_joined = vents['date_joined'] 
                    adjustment.store_id = vents['store']
                    adjustment.observation = vents['observation']
                    adjustment.save()
                    for i in vents['products']:
                        det = DetAdjustment()
                        inve = Inventory() 
                        storeProdStock = StoreProdStock()
                        det.adjustment_id = adjustment.id
                        det.prod_id = i['id']
                        det.types = int(i['type'])
                        det.amount = int(i['amount'])
                        print(i['type'])
                        print(vents['store'])
                        if str(i['type'])=='0' and str(vents['store'])=='1':
                            print('en la primera')
                            det.store1_previous = int(i['stock'])
                            det.store1_next = int(i['stock']) + int(i['amount'])
                        elif str(i['type'])=='1' and str(vents['store'])=='1':
                            print('en la segunda')
                            det.store1_previous = int(i['stock'])
                            det.store1_next = int(i['stock']) - int(i['amount'])
                        elif str(i['type'])=='0' and str(vents['store'])=='2':
                            print('en la tercera')
                            det.store2_previous = int(i['stock'])
                            det.store2_next = int(i['stock']) + int(i['amount'])
                        elif str(i['type'])=='1' and str(vents['store'])=='2':
                            print('en la cuarta')
                            det.store2_previous = int(i['stock'])
                            det.store2_next = int(i['stock']) - int(i['amount'])
                        inve.prod_id = i['id']
                        inve.in_store_id = vents['store']
                        inve.out_store_id = vents['store']
                        inve.stock = int(i['amount'])
                        inve.types = 4
                        inve.operaAdjustment_id = adjustment.id                                                
                        inve.save()                        
                        det.save() 
                        storeProdStock = StoreProdStock.objects.get(store__in=[vents['store']], prod__in=[i['id']])
                        if i['type']==0:
                            storeProdStock.stock_in += det.amount
                            storeProdStock.save()
                            det.prod.stock += det.amount
                            det.prod.save()
                        else:
                            storeProdStock.stock_in -= det.amount
                            storeProdStock.save()
                            det.prod.stock -= det.amount
                            det.prod.save()
                        

                    data = {'id': adjustment.id}

                                         
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de un Adjuste'
        context['entity'] = 'Adjustes'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['det'] = []
        return context


 

class AdjustmentDeleteView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Adjustment
    template_name = 'adjustment/delete.html'
    success_url = reverse_lazy('adjustment_list')
    permission_required = 'delete_adjustment'
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
        context['title'] = 'Eliminación de un adjuste'
        context['entity'] = 'Adjustes'
        context['list_url'] = self.success_url
        return context


class AdjustmentInvoicePdfView(Configuration, View):

    def link_callback(self, uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        # use short variable names
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /static/media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri  # handle absolute uri (ie: http://some.tld/foo.png)

        # make sure that file exists
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('adjustment/invoice.html')
            context = {
                'adjustment': Adjustment.objects.get(pk=self.kwargs['pk']),
                'comp': {'name': 'INVERSIONES ANLIL 2022, C.A', 'ruc': 'J503126132', 'address': 'CALLE ESQUINA CALLE 12 CON CARRERA 19 LOCAL LOCAL COMERCIAL NRO 19 06 BARRIO BARRIO OBRERO SAN CRISTOBAL TACHIRA ZONA POSTAL 5001'},
                'icon': '{}{}'.format(settings.STATIC_URL, 'img/barras.jpeg')
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
            pisaStatus = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback
            )
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('adjustment_list'))

