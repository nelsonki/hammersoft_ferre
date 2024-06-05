import json
import os
from django.conf import settings
from datetime import datetime
import pytz
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms.models import BaseModelForm

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.erp.forms import ClientForm, InputForm
from core.erp.mixins import Configuration, ValidatePermissionRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, TemplateView

from core.erp.models import Client, DetProdCombo, Input, ProdCombo, Product, DetInput, Inventory, StoreProdStock
from django.template.loader import get_template

from xhtml2pdf import pisa

from core.erp.forms import InputForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from django.db.models import Q


from datetime import datetime
from django.db.models import Sum



class InputListView(Configuration,LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Input
    form_class = InputForm
    template_name = 'input/list.html'
    permission_required = 'view_input'
    url_redirect = reverse_lazy('dashboard')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    
    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        print(action)
        if action == 'searchdata':
            data = []
            for i in Input.objects.all():
                data.append(i.toJSON())
        elif action == 'search_details_prod':
            data = []
            for i in DetInput.objects.filter(input_id=request.POST['id']):
                data.append(i.toJSON())
        elif action == 'search_time':
            with transaction.atomic():
                tz = pytz.timezone('America/Caracas')
                fecha = datetime.now(tz).strftime('%Y-%m-%d %H:%M')
                frmTime = json.loads(request.POST['time'])
                print(fecha)
                print(frmTime['date_reminder'])
                input = Input.objects.get(id=request.POST['id'])
                if frmTime['status'] == '1':
                    input.date_pay = fecha
                    input.status = frmTime['status']
                else:
                    input.date_pay = None    
                    input.status = frmTime['status']
                    input.date_reminder = frmTime['date_reminder']            
                input.save()
        else:
            data['error'] = 'Ha ocurrido un error'
         
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Entradas'
        context['create_url'] = reverse_lazy('input_create')
        context['list_url'] = reverse_lazy('input_list')
        context['entity'] = 'Entradas'
        context['action'] = 'edit'

        context['frmTime'] = InputForm()

        return context


class InputCreateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Input
    form_class = InputForm
    template_name = 'input/create.html'
    success_url = reverse_lazy('input_list')
    permission_required = 'add_input'
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
                ids_exclude = json.loads(request.POST['ids'])
                term = request.POST['term'].strip()
                products = Product.objects.filter(Q(cate__isnull=False) | Q(cate__name__isnull=False)).exclude(is_combo=1)
                if len(term):
                    products = products.filter(name__icontains=term)
                for i in products.filter(store__in='1').exclude(id__in=ids_exclude)[0:10]:
                    storeProdStock = StoreProdStock.objects.get(store__in=[1], prod__in=[i.id])
                    item = i.toJSON()
                    item['value'] = i.name
                    item['stock'] = storeProdStock.stock_in
                    data.append(item)
            elif action == 'add':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    print(vents)
                    input = Input()
                    input.date_joined = vents['date_joined'] 
                    input.cli_id = vents['cli']
                    input.tipoFacNot = vents['tipoFacNot']
                    input.num_liquidacion = vents['num_liquidacion']
                    input.store_id = 1
                    input.subtotal = float(vents['subtotal'])
                    input.tax = float(vents['tax'])
                    input.total = float(vents['total'])
                    input.save()
                    for i in vents['products']:
                        det = DetInput()
                        inve = Inventory()
                        storeProdStock = StoreProdStock()
                        det.input_id = input.id
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.costBs = float(i['costBs'])
                        det.rate = float(i['rate'])
                        det.cost = float(i['price_in'])
                        det.subtotal = float(i['subtotal'])
                        inve.prod_id = i['id']
                        inve.in_store_id = 1
                        inve.out_store_id = 1
                        inve.stock = int(i['amount'])
                        inve.types = '1'
                        inve.operaIn_id = input.id
                        inve.save()
                        det.save()
                        det.prod.stock = det.amount
                        det.prod.price_in = det.cost
                        det.prod.save()
                        storeProdStock = StoreProdStock.objects.get(store__in=[1], prod__in=[i['id']])
                        storeProdStock.stock_in += det.amount
                        storeProdStock.save()             
                    data = {'id': input.id}
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
        context['title'] = 'Creación de una Entrada'
        context['entity'] = 'Entradas'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['frmClient'] = ClientForm()
        context['det'] = []
        return context


class InputUpdateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Input
    form_class = InputForm
    template_name = 'input/create.html'
    success_url = reverse_lazy('input_list')
    permission_required = 'change_input'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None ):
        instance = self.get_object()
        form = InputForm(instance=instance)
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
                    Input = self.get_object()
                    Input.date_joined = vents['date_joined'] 
                    Input.cli_id = vents['cli']
                    Input.store_id = vents['store']
                    Input.subtotal = float(vents['subtotal'])
                    Input.tax = float(vents['tax'])
                    Input.total = float(vents['total'])
                    Input.save()
                    for i in vents['products']:
                        det = DetInput()                        
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.prod.stock += det.amount
                        det.prod.save()
                    Input.detinput_set.all().delete()
                    Inventory.objects.filter(operaOut_id=Input.id).all().delete()
                    for i in vents['products']:
                        det = DetInput()                        
                        det.input_id = Input.id
                        det.prod_id = i['id']
                        det.amount = int(i['amount'])
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])                      
                        inve.prod_id = i['id']
                        inve.store_id = vents['store']
                        inve.stock = int(i['amount'])
                        inve.types = '2'
                        inve.operaOut_id = Input.id  
                        det.save()
                        inve.save()                        
                        det.prod.stock += det.amount
                        det.prod.save()
                    data = {'id': Input.id}
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
           for i in DetInput.objects.filter(input_id=self.get_object().id):
               item = i.prod.toJSON()
               item['amount'] =i.amount
               data.append(item)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar una Entrada'
        context['entity'] = 'Entradas'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['frmClient'] = ClientForm()
        context['det'] = json.dumps(self.get_details_product())
        return context
 

class InputDeleteView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Input
    template_name = 'input/delete.html'
    success_url = reverse_lazy('input_list')
    permission_required = 'delete_input'
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
        context['title'] = 'Eliminación de una Entrada'
        context['entity'] = 'Entrada'
        context['list_url'] = self.success_url
        return context


class InputInvoicePdfView(Configuration, View):

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
            template = get_template('input/invoice.html')
            context = {
                'input': Input.objects.get(pk=self.kwargs['pk']),
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
        return HttpResponseRedirect(reverse_lazy('input_list'))


class InputGraficView(Configuration, TemplateView):
    template_name = 'input/grafic.html'

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
            if action == 'get_graph_input_year_month':
                data = {
                    'name': 'Porcentaje de Compras',
                    'showInLegend': False,
                    'colorByPoint': True,
                    'data': self.get_graph_input_year_month()
                }
            elif action == 'get_graph_input_products_year_month':
                data = {
                    'name': 'Porcentaje',
                    'colorByPoint': True,
                    'data': self.get_graph_input_products_year_month(),
                }
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_graph_input_year_month(self):
        data = []
        try:
            year = datetime.now().year
            for m in range(1, 13):
                total = Input.objects.filter(date_joined__year=year, date_joined__month=m).aggregate(total=Sum('total')).get('total') or 0                                                                                           
                data.append(float(total))
        except:
            pass
        return data

    def get_graph_input_products_year_month(self):
        data = []
        year = datetime.now().year
        month = datetime.now().month
        try:
            for p in Product.objects.filter(Q(cate__isnull=False) | Q(cate__name__isnull=False)):
                total = DetInput.objects.filter(input__date_joined__year=year, input__date_joined__month=month,
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
        context['get_graph_input_year_month'] = self.get_graph_input_year_month()
        context['get_graph_input_products_year_month'] = self.get_graph_input_products_year_month()

        return context