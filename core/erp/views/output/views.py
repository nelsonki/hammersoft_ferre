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

from core.erp.models import Client, DetProdCombo, Output, ProdCombo, Product, DetOutput, Inventory, StoreProdStock
from django.template.loader import get_template

from xhtml2pdf import pisa

from core.erp.forms import OutputForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from django.db.models import Q

from datetime import datetime
from django.db.models import Sum

class OutputListView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Output
    template_name = 'output/list.html'
    permission_required = 'view_output'
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
                for i in Output.objects.all():
                    data.append(i.toJSON())
            elif action == 'search_details_prod':
                data = []
                for i in DetOutput.objects.filter(output_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Salidas'
        context['create_url'] = reverse_lazy('output_create')
        context['list_url'] = reverse_lazy('output_list')
        context['entity'] = 'Salidas'
        return context


class OutputCreateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Output
    form_class = OutputForm
    template_name = 'output/create.html'
    success_url = reverse_lazy('output_list')
    permission_required = 'add_output'
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
                    products = Product.objects.filter(Q(cate__isnull=False) | Q(cate__name__isnull=False))
                    if len(term):
                        products = products.filter(name__icontains=term)
                    for i in products.filter(store__in=storeViene).exclude(id__in=ids_exclude)[0:10]:                        
                        storeProdStock = StoreProdStock.objects.get(store__in=[storeViene], prod__in=[i.id])  
                        print(storeProdStock.stock_in)
                        print(i.is_combo)
                        if (storeProdStock.stock_in > 0 and i.is_combo==0) or (i.pvp > 0 and i.is_combo==1):                       
                            item = i.toJSON()
                            item['value'] = i.name
                            item['stock'] = storeProdStock.stock_in
                            data.append(item) 
   
            elif action == 'add':
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
                                    det.prod.stock -= (itemj['amount'] * det.amount)
                                    det.prod.save()
                        else:    
                            storeProdStock = StoreProdStock.objects.get(store__in=[vents['store']], prod__in=[i['id']])
                            storeProdStock.stock_in -= det.amount
                            storeProdStock.save()
                            det.prod.stock -= det.amount
                            det.prod.save()
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
            elif action == 'validateCombo': 
                    print('si entro en validateCombo')
                    prod =json.loads(request.POST['idsProd'])
                    for a in prod:
                        print(a)
                        if a['is_combo']==1:              
                            prodcombo = ProdCombo.objects.filter(prod_id=a['id'])
                            for item in prodcombo:
                                detprodcombo =DetProdCombo.objects.filter(prodcombo_id=item.id)
                                for det_item  in detprodcombo:
                                    cant = a['amount'] * det_item.amount
                                    storeProdStock = StoreProdStock.objects.get(store__in=['1'], prod__in=[det_item.prod_id])
                                    print(storeProdStock.id)
                                    if storeProdStock.stock_in < cant:
                                        data['error'] = "Para el combo: {}, no hay suficientes:   .-{}".format(a['name'], storeProdStock.prod.name)
                                         
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de una Salida'
        context['entity'] = 'Salidas'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['frmClient'] = ClientForm()
        context['det'] = []
        return context


class OutputUpdateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):#no se esta usando
    model = Output
    form_class = OutputForm
    template_name = 'output/create.html'
    success_url = reverse_lazy('output_list')
    permission_required = 'change_output'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None ):
        instance = self.get_object()
        form = OutputForm(instance=instance)
        form.fields['cli'].queryset = Client.objects.filter(id=instance.cli.id)
        return form
    
    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products': 
                data = [] 
                storeViene =request.POST['vaStore']
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
            elif action == 'edit':
                with transaction.atomic():
                    inve = Inventory()
                    vents = json.loads(request.POST['vents'])
                    output = self.get_object()
                    output.date_joined = vents['date_joined'] 
                    output.cli_id = vents['cli']
                    output.store_id = vents['store']
                    output.subtotal = float(vents['subtotal'])
                    output.tax = float(vents['tax'])
                    output.total = float(vents['total'])
                    output.save()
                    for i in vents['products']:
                        det = DetOutput()                        
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.prod.stock += det.amount
                        det.prod.save()
                    output.detoutput_set.all().delete()
                    Inventory.objects.filter(operaOut_id=output.id).all().delete()
                    for i in vents['products']:
                        det = DetOutput()                        
                        det.output_id = output.id
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])                      
                        inve.prod_id = i['id']
                        inve.store_id = vents['store']
                        inve.stock = int(i['amount'])
                        inve.types = 2
                        inve.operaOut_id = output.id  
                        det.save()
                        inve.save()                        
                        det.prod.stock -= det.amount
                        det.prod.save()
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
           for i in DetOutput.objects.filter(output_id=self.get_object().id):
               item = i.prod.toJSON()
               item['amount'] =i.amount
               data.append(item)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar una Salida'
        context['entity'] = 'Salidas'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['frmClient'] = ClientForm()
        context['det'] = json.dumps(self.get_details_product())
        return context
 

class OutputDeleteView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Output
    template_name = 'output/delete.html'
    success_url = reverse_lazy('output_list')
    permission_required = 'delete_output'
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
        context['title'] = 'Eliminación de una Salida'
        context['entity'] = 'Salida'
        context['list_url'] = self.success_url
        return context


class OutputInvoicePdfView(Configuration, View):

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
            template = get_template('output/invoice.html')
            context = {
                'output': Output.objects.get(pk=self.kwargs['pk']),
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
        return HttpResponseRedirect(reverse_lazy('output_list'))

class OutputGraficView(Configuration, TemplateView):
    template_name = 'output/grafic.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        request.user.get_group_session()
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'get_graph_output_year_month':
                data = {
                    'name': 'Porcentaje de Compras',
                    'showInLegend': False,
                    'colorByPoint': True,
                    'data': self.get_graph_output_year_month()
                }
            elif action == 'get_graph_output_products_year_month':
                data = {
                    'name': 'Porcentaje',
                    'colorByPoint': True,
                    'data': self.get_graph_output_products_year_month(),
                }
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_graph_output_year_month(self):
        data = []
        try:
            year = datetime.now().year
            for m in range(1, 13):
                total = Output.objects.filter(date_joined__year=year, date_joined__month=m).aggregate(total=Sum('total')).get('total') or 0                                                                                           
                data.append(float(total))
        except:
            pass
        return data

    def get_graph_output_products_year_month(self):
        data = []
        year = datetime.now().year
        month = datetime.now().month
        try:
            for p in Product.objects.filter(Q(cate__isnull=False) | Q(cate__name__isnull=False)):
                print(p.id)
                total = DetOutput.objects.filter(output__date_joined__year=year, output__date_joined__month=month,
                                               prod_id=p.id).aggregate(subtotal=Sum('subtotal')).get('subtotal') or 0   
                if total > 0:
                    data.append({
                        'name': p.name,
                        'y': float(total)
                    })
        except:
            pass
        return data
    
    def product_stock_min_count(self):
        count_stock_min =0
        for g in Product.objects.filter(Q(cate__isnull=False) | Q(cate__name__isnull=False)):
            prod_stock_min = g.stock_min
            product_stock_general = StoreProdStock.objects.filter(prod_id=g.id).aggregate(stock_in=Sum('stock_in')).get('stock_in') or 0 
            if(prod_stock_min > product_stock_general):
                count_stock_min +=1  
        return count_stock_min

    
    def year(self):
        year = datetime.now().year
        return year
    
    def month(self):
        month = datetime.now().month
        return month

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alert_stock_mim'] = self.product_stock_min_count()
        context['year'] = self.year()
        context['month'] = self.month()
        context['get_graph_output_year_month'] = self.get_graph_output_year_month()
        context['get_graph_output_products_year_month'] = self.get_graph_output_products_year_month()

        return context