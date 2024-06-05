import json
import os
from django.conf import settings
from datetime import datetime
import pytz
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms.models import BaseModelForm
import smtplib
from django.template.loader import render_to_string

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.erp.forms import ClientForm, ClosingForm
from core.erp.mixins import Configuration, ValidatePermissionRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, TemplateView

from core.erp.models import Client,  Closing, DetOutput, Input, Output,  Product,  StoreProdStock
from django.template.loader import get_template

from xhtml2pdf import pisa

from core.erp.forms import ClosingForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from django.db.models import Q

from datetime import datetime
from django.db.models import Sum

class ClosingListView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Closing
    template_name = 'closing/list.html'
    permission_required = 'view_closing'
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
                for i in Closing.objects.all():
                    data.append(i.toJSON())
            elif action == 'search_report':                 
                        dataA = []
                        idClosing = request.POST.get('misDatos', '')
                        print(idClosing)              
                        closing = Closing.objects.get(id=idClosing)
                        print(closing)
                        start_date = closing.date_in           
                        end_date = closing.date_end  
                        correo = request.POST.get('correo', '')               
                        num_fact_list = list(map(int, closing.num_input.split(',')))
                        if len(num_fact_list)==1:
                            search = DetOutput.objects.filter(output_id=closing.num_input).values('prod__code','prod__name')
                            search = search.annotate(amount=Sum('amount'))
                            search = search.annotate(subtotal=Sum('subtotal'))
                            search = search.order_by('amount')
                        else:
                            output_ids = Output.objects.filter(id__in=num_fact_list).values_list('id', flat=True)
                            search = output_ids.filter(created_at__range=[start_date, end_date])
                            search = DetOutput.objects.all().filter(output_id__in=output_ids).values('prod__code','prod__name')
                            search = search.annotate(amount=Sum('amount'))
                            search = search.annotate(subtotal=Sum('subtotal'))
                            search = search.order_by('amount')
                        for s in search:
                            dataA.append([
                                s['prod__code'],
                                s['prod__name'],
                                s['amount'],
                                format(s['subtotal'], '.2f'),
                            ])
                        #almenos una venta asociada .filter(output__isnull=False)
                        if correo:
                            print('me estas enviando un correo dentro del search_report')                             
                            URL = settings.DOMAIN if not settings.DEBUG else self.request.META['HTTP_HOST']                
                            mailServer = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                            mailServer.starttls()
                            mailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

                            email_to = correo
                            mensaje = MIMEMultipart()
                            mensaje['From'] = settings.EMAIL_HOST_USER
                            mensaje['To'] = email_to
                            mensaje['Subject'] = 'Reporte'

                            content = render_to_string('closing/miReporteCierre.html', {
                                'closing': closing,
                                'comp': {'name': 'INVERSIONES ANLIL 2022, C.A', 'ruc': 'J503126132', 'address': 'CALLE ESQUINA CALLE 12 CON CARRERA 19 LOCAL LOCAL COMERCIAL NRO 19 06 BARRIO BARRIO OBRERO SAN CRISTOBAL TACHIRA ZONA POSTAL 5001'},
                                'detClosing': dataA,
                            })
                            mensaje.attach(MIMEText(content, 'html'))

                            mailServer.sendmail(settings.EMAIL_HOST_USER,
                                                email_to,
                                                mensaje.as_string()) 
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Cierres de salidas'
        context['create_url'] = reverse_lazy('closing_create')
        context['list_url'] = reverse_lazy('closing_list')
        context['entity'] = 'Cierres'
        return context


class ClosingCreateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Closing
    form_class = ClosingForm
    template_name = 'closing/create.html'
    success_url = reverse_lazy('closing_list')
    permission_required = 'add_closing'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']          
        if action == 'search_report':
                data = []
                start_date = request.POST.get('data_in', '')
                end_date = request.POST.get('data_end', '')
                print(start_date)
                search = Output.objects.all().exclude(status=1)
                if len(start_date) and len(end_date):
                    search = search.filter(date_joined__range=[start_date, end_date])
                for s in search:
                    item = s.toJSON()
                    item['date_joined'] = s.date_joined.strftime('%Y-%m-%d %H:%M')
                    item['total'] = format(s.total, '.2f')
                    data.append(item)
        elif action == 'add':
                with transaction.atomic():
                    tz = pytz.timezone('America/Caracas')
                    fecha = datetime.now(tz).strftime('%Y-%m-%d %H:%M')
                    ''' print(request.POST['observation'])
                    print(request.POST['total'])
                    print(request.POST['dolar'])
                    print(request.POST['peso'])
                    print(request.POST['bolivar'])
                    print(request.POST['data_in'])
                    print(request.POST['data_end'])'''
                    # Deserializa 'misFacturas' de una cadena JSON a una lista de diccionarios en Python
                    misFacturas = json.loads(request.POST['misFacturas'])
                    cant_facturas=0
                    num_fact=''
                    for factura in misFacturas:
                        output = Output.objects.get(id=factura.get('id'))
                        output.status = 1
                        output.save()
                        cant_facturas+=1
                        # Ahora 'factura' es un diccionario en Python, no una cadena JSON
                        item = json.dumps(factura)
                        num_fact += str(factura.get('id')) + ',' # Agrega el id de la factura a la cadena 'num_fact'
                    closing = Closing()
                    closing.date_joined = fecha
                    closing.date_in = request.POST['data_in']  
                    closing.date_end = request.POST['data_end']  
                    closing.num_input = num_fact[:-1]# Elimina la coma final de la cadena
                    closing.cant_input = cant_facturas
                    closing.observation = request.POST['observation']
                    closing.total = float(request.POST['total'])
                    closing.dolar = float(request.POST['dolar'])
                    closing.peso = float(request.POST['peso'])
                    closing.bolivar = float(request.POST['bolivar'])
                    closing.save()                     
                    data = {'id': closing.id}
                
        else:
                data['error'] = 'No ha ingresado a ninguna opción'
        
        return JsonResponse(data, safe=False)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de un cierre de salidas'
        context['entity'] = 'Cierres'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['det'] = []
        context['form'] = ClosingForm()

        return context


class ClosingUpdateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):#no se esta usando
    model = Closing
    form_class = ClosingForm
    template_name = 'closing/create.html'
    success_url = reverse_lazy('closing_list')
    permission_required = 'change_closing'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
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
                    tz = pytz.timezone('America/Caracas')
                    fecha = datetime.now(tz).strftime('%Y-%m-%d %H:%M')
                    print(request.POST['observation'])
                    print(request.POST['total'])
                    print(request.POST['dolar'])
                    print(request.POST['peso'])
                    print(request.POST['bolivar'])
                    print(request.POST['data_in'])
                    print(request.POST['data_end'])
                    # Deserializa 'misFacturas' de una cadena JSON a una lista de diccionarios en Python
                    misFacturas = json.loads(request.POST['misFacturas'])
                    cant_facturas=0
                    num_fact=''
                    for factura in misFacturas:
                        output = Output.objects.get(id__in=str(factura.get('id')))
                        output.status = 1
                        output.save()
                        cant_facturas+=1
                        # Ahora 'factura' es un diccionario en Python, no una cadena JSON
                        item = json.dumps(factura)
                        num_fact += str(factura.get('id')) + ',' # Agrega el id de la factura a la cadena 'num_fact'
                    closing = Closing()
                    closing.date_joined = fecha
                    closing.date_in = request.POST['data_in']  
                    closing.date_end = request.POST['data_end']  
                    closing.num_input = num_fact[:-1]# Elimina la coma final de la cadena
                    closing.cant_input = cant_facturas
                    closing.observation = request.POST['observation']
                    closing.total = float(request.POST['total'])
                    closing.dolar = float(request.POST['dolar'])
                    closing.peso = float(request.POST['peso'])
                    closing.bolivar = float(request.POST['bolivar'])
                    closing.save()                     
                    data = {'id': closing.id}
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)
    
    def get_rango_fecha(self):
        data=[]
        try:
           for i in Closing.objects.filter(id=self.get_object().id):
               item = i.toJSON()
               data.append(item)
               print(data)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar un cierre de Salidas'
        context['entity'] = 'Cierres'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['det'] = json.dumps(self.get_rango_fecha())

        return context
 

class ClosingDeleteView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Closing
    template_name = 'closing/delete.html'
    success_url = reverse_lazy('closing_list')
    permission_required = 'delete_closing'
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
        context['title'] = 'Eliminación de un cierre'
        context['entity'] = 'Cierres'
        context['list_url'] = self.success_url
        return context

class ClosingInvoicePdfView(Configuration, View):

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
            template = get_template('closing/invoice.html')
            dataA = []
            closing = Closing.objects.get(pk=self.kwargs['pk'])
            start_date = closing.date_in           
            end_date = closing.date_end  
            num_fact_list = list(map(int, closing.num_input.split(',')))
            if len(num_fact_list)==1:
                search = DetOutput.objects.filter(output_id=closing.num_input).values('prod__code','prod__name')
                search = search.annotate(amount=Sum('amount'))
                search = search.annotate(subtotal=Sum('subtotal'))
                search = search.order_by('amount')
            else:
                output_ids = Output.objects.filter(id__in=num_fact_list).values_list('id', flat=True)
                search = output_ids.filter(created_at__range=[start_date, end_date])
                search = DetOutput.objects.all().filter(output_id__in=output_ids).values('prod__code','prod__name')
                search = search.annotate(amount=Sum('amount'))
                search = search.annotate(subtotal=Sum('subtotal'))
                search = search.order_by('amount')
            for s in search:
                dataA.append([
                    s['prod__code'],
                    s['prod__name'],
                    s['amount'],
                    format(s['subtotal'], '.2f'),
                ])
            context = {
                'closing': Closing.objects.get(pk=self.kwargs['pk']),
                'detClosing': dataA,
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
        except Exception as e:
            pass
        return HttpResponseRedirect(reverse_lazy('closing_list'))
    
