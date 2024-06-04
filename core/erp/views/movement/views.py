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

from core.erp.forms import ClientForm, MovementForm
from core.erp.mixins import Configuration, ValidatePermissionRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, UpdateView

from core.erp.models import Client, Movement, Product, DetMov, Inventory, StoreProdStock
from django.template.loader import get_template

from xhtml2pdf import pisa

from core.erp.mixins import ValidatePermissionRequiredMixin
from django.db.models import Q

class MovementListView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Movement
    template_name = 'movement/list.html'
    permission_required = 'view_movement'
    url_redirect = reverse_lazy('dashboard')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        if action == 'searchdata':
                data = []
                for i in Movement.objects.all():
                    data.append(i.toJSON())
        elif action == 'search_details_prod':
                data = []
                for i in DetMov.objects.filter(movement_id=request.POST['id']):
                    data.append(i.toJSON())
        else:
                data['error'] = 'Ha ocurrido un error'
         
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Movimientos'
        context['create_url'] = reverse_lazy('movement_create')
        context['list_url'] = reverse_lazy('movement_list')
        context['entity'] = 'Movimientos'
        return context


class MovementCreateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Movement
    form_class = MovementForm
    template_name = 'movement/create.html'
    success_url = reverse_lazy('movement_list')
    permission_required = 'add_movement'
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
                    products = Product.objects.filter(stock__gt=0)
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
                    print(vents)
                    movement = Movement()
                    movement.date_joined = vents['date_joined'] 
                    movement.in_store_id = vents['in_store']
                    movement.out_store_id = vents['out_store']
                    movement.description = vents['description']
                    movement.save()
                    for i in vents['products']:
                        det = DetMov()
                        inve = Inventory()
                        storeProdStock = StoreProdStock()
                        det.movement_id = movement.id
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        inve.prod_id = i['id']
                        inve.in_store_id = movement.in_store_id
                        inve.out_store_id = movement.out_store_id
                        inve.types = '3'
                        inve.operaMove_id = movement.id
                        inve.stock = det.amount
                        inve.save()
                        det.save()
                        det.prod.stock += det.amount
                        det.prod.save()
                        storeProdStock = StoreProdStock.objects.get(store__in=[movement.in_store_id], prod__in=[i['id']])
                        storeProdStock.stock_in -= det.amount
                        storeProdStock.save()
                        storeProdStock = StoreProdStock.objects.get(store__in=[movement.out_store_id], prod__in=[i['id']])
                        storeProdStock.stock_in += det.amount
                        storeProdStock.save()
                        #if StoreProdStock.objects.filter(Q(store__in=[1]) & Q(prod__in=[i['id']])):
                           # storeProdStock.stock_in += det.amount 
                            #storeProdStock.save()                 
                    data = {'id': movement.id}
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de un Movimiento'
        context['entity'] = 'Movimientos'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['det'] = []
        return context


class MovementUpdateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Movement
    form_class = MovementForm
    template_name = 'movement/create.html'
    success_url = reverse_lazy('movement_list')
    permission_required = 'change_movement'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None ):
        instance = self.get_object()
        form = MovementForm(instance=instance)
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
                products = Product.objects.filter(stock__gt=0)
                if len(term):
                    products = products.filter(name__icontains=term)
                for i in products.exclude(id__in=ids_exclude)[0:10]:
                    item = i.toJSON()
                    item['value'] = i.name
                    # item['text'] = i.name
                    data.append(item)
            elif action == 'edit':
                with transaction.atomic():
                    inve = Inventory()
                    vents = json.loads(request.POST['vents'])
                    Movement = self.get_object()
                    Movement.date_joined = vents['date_joined'] 
                    Movement.cli_id = vents['cli']
                    Movement.store_id = vents['store']
                    Movement.subtotal = float(vents['subtotal'])
                    Movement.tax = float(vents['tax'])
                    Movement.total = float(vents['total'])
                    Movement.save()
                    for i in vents['products']:
                        det = DetMov()                        
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.prod.stock += det.amount
                        det.prod.save()
                    Movement.detmov_set.all().delete()
                    Inventory.objects.filter(operaOut_id=Movement.id).all().delete()
                    for i in vents['products']:
                        det = DetMov()                        
                        det.movement_id = Movement.id
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])                      
                        inve.prod_id = i['id']
                        inve.store_id = vents['store']
                        inve.stock = int(i['amount'])
                        inve.types = '2'
                        inve.operaOut_id = Movement.id  
                        det.save()
                        inve.save()                        
                        det.prod.stock += det.amount
                        det.prod.save()
                    data = {'id': Movement.id}
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
           for i in DetMov.objects.filter(movement_id=self.get_object().id):
               item = i.prod.toJSON()
               item['amount'] =i.amount
               data.append(item)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar un Movimiento'
        context['entity'] = 'Movimientos'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['frmClient'] = ClientForm()
        context['det'] = json.dumps(self.get_details_product())
        return context
 

class MovementDeleteView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Movement
    template_name = 'movement/delete.html'
    success_url = reverse_lazy('movement_list')
    permission_required = 'delete_movement'
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
        context['title'] = 'Eliminación de un Movimiento'
        context['entity'] = 'Movimiento'
        context['list_url'] = self.success_url
        return context


class MovementInvoicePdfView(Configuration, View):

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
            template = get_template('movement/invoice.html')
            context = {
                'movement': Movement.objects.get(pk=self.kwargs['pk']),
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
        return HttpResponseRedirect(reverse_lazy('movement_list'))
