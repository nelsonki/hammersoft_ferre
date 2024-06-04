from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from core.erp.mixins import Configuration
from core.erp.models import Config, DetOutput, Inventory, Product,Output, StoreProd, StoreProdStock
from core.reports.forms import ReportForm
from django.db.models import Sum, F, Q, Value, Subquery, OuterRef
from django.conf import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.http import  JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from itertools import chain
from django.db.models import Q

class ReportInventaryView(Configuration, TemplateView):
    template_name = 'inventary/report.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_report':
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')          
                correo = request.POST.get('correo', '')
                search = Inventory.objects.values('created_at','types','stock','prod__name','in_store__name','out_store__name')
                #.values('prod_id', 'types', 'store_id'   ).annotate(stock=Sum('stock'))#agrupa por lo que este dentro de valores
                if len(start_date) and len(end_date):
                    search = search.filter(created_at__range=[start_date, end_date])
                for s in search:
                     tipo = "Entrada" if s['types'] == '1' else "Salida" if s['types'] == '2' else "Movimiento" if s['types'] == '3' else "Adjuste"
                     data.append([
                        s['created_at'].strftime('%Y-%m-%d %H:%M'),
                        s['in_store__name'],
                        s['out_store__name'],
                        tipo,
                        s['prod__name'],
                        s['stock'],
                    ])
                    
                if correo:
                    print(data)
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

                    content = render_to_string('inventary/miReporteCorreo.html', {
                        'desde':start_date, 
                        'hasta':end_date,
                        'comp': {'name': 'INVERSIONES ANLIL 2022, C.A', 'ruc': 'J503126132', 'address': 'CALLE ESQUINA CALLE 12 CON CARRERA 19 LOCAL LOCAL COMERCIAL NRO 19 06 BARRIO BARRIO OBRERO SAN CRISTOBAL TACHIRA ZONA POSTAL 5001'},
                        'data': data,
                    })
                    mensaje.attach(MIMEText(content, 'html'))

                    mailServer.sendmail(settings.EMAIL_HOST_USER,
                                        email_to,
                                        mensaje.as_string()) 
             
                print(data)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)
    
    # función que filtra los resultados por prod_id
    def obtener_stock_general(id_producto):
        stock_general = StoreProdStock.objects.all().values('prod_id').annotate(stock_in=Sum('stock_in'))
        # Filtrar la respuesta por el id del producto
        resultado = list(filter(lambda item: item['prod_id'] == id_producto, stock_general))
        return resultado
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Inventario por operaciones'
        context['entity'] = 'Reportes'
        context['list_url'] = reverse_lazy('inventary_report')
        context['form'] = ReportForm()
        return context


class ReportProductOutputView(Configuration,  TemplateView):
    template_name = 'inventary/reportProductOutput.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_report':
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')          
                correo = request.POST.get('correo', '')               
                output_ids = Output.objects.values_list('id', flat=True)
                search = DetOutput.objects.all().filter(output_id__in=output_ids).values('prod__code','prod__name')
                if len(start_date) and len(end_date):
                    search = search.filter(created_at__range=[start_date, end_date])
                search = search.annotate(amount=Sum('amount'))
                search = search.annotate(subtotal=Sum('subtotal'))
               # search = search.annotate(total_price=F("amount") * F('price'))
                search = search.order_by('amount')
                print(search)
                for s in search:
                     data.append([
                        s['prod__code'],
                        s['prod__name'],
                        s['amount'],
                        format(s['subtotal'], '.2f'),
                       # format(s['total_price'], '.2f'),
                    ])
                total_sum = search.aggregate(Sum('subtotal'))['subtotal__sum']
                if total_sum:
                    data.append([
                        '---',
                        '---',
                        'Total en Dolares:',                  
                        format(total_sum, '.2f'),
                    ])
                    items = Config.objects.all()
                    for item in items:
                        totalPesos = total_sum * item.cambioVentaDolarCop
                        totalBolivares = total_sum * item.cambioVentaDolarBs
                        data.append([
                            '---',
                            '---',
                            'Total en Pesos:',                  
                            format(totalPesos, '.2f'),
                        ])
                        data.append([
                            '---',
                            '---',
                            'Total en Bolivares:',                  
                            format(totalBolivares, '.2f'),
                        ])

               #almenos una venta asociada .filter(output__isnull=False)
                if correo:
                    print(data)
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

                    content = render_to_string('inventary/miReporteCorreoProd.html', {
                        'desde':start_date, 
                        'hasta':end_date,
                        'comp': {'name': 'INVERSIONES ANLIL 2022, C.A', 'ruc': 'J503126132', 'address': 'CALLE ESQUINA CALLE 12 CON CARRERA 19 LOCAL LOCAL COMERCIAL NRO 19 06 BARRIO BARRIO OBRERO SAN CRISTOBAL TACHIRA ZONA POSTAL 5001'},
                        'data': data,
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
    
    # función que filtra los resultados por prod_id
    def obtener_stock_general(id_producto):
        stock_general = StoreProdStock.objects.all().values('prod_id').annotate(stock_in=Sum('stock_in'))
        # Filtrar la respuesta por el id del producto
        resultado = list(filter(lambda item: item['prod_id'] == id_producto, stock_general))
        return resultado
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de ventas por producto'
        context['entity'] = 'Reportes'
        context['list_url'] = reverse_lazy('inventaryprod_report')
        context['form'] = ReportForm()
        return context


class ReportProductStoreView(Configuration, TemplateView):
    template_name = 'inventary/reportProductStore.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_report':
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')          
                correo = request.POST.get('correo', '')   
                prod_ids = Product.objects.filter(Q(cate__isnull=False) | Q(cate__name__isnull=False)).values_list('id', flat=True) #se puede cambiar para que se coloque el id del producto

                stock_1 = StoreProdStock.objects.filter(Q(prod_id__in=prod_ids) & Q(store_id=1)).values('prod__code','prod__name').annotate(stock1=Sum('stock_in')) 
                stock_2 = StoreProdStock.objects.filter(Q(prod_id__in=prod_ids) & Q(store_id=2)).values('prod__code','prod__name').annotate(stock2=Sum('stock_in'))
                for s in stock_1:
                    stock2=0
                    total=0
                    for s2 in stock_2:
                        if s['prod__code'] == s2['prod__code']:
                            stock2=s2['stock2']
                            total=s['stock1']+s2['stock2']
                    data.append([
                        s['prod__code'],
                        s['prod__name'],
                        total,
                        s['stock1'],
                        stock2,                        
                    ])
                print(data)
               #almenos una venta asociada .filter(output__isnull=False)
                '''if correo:
                    print(data)
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

                    content = render_to_string('inventary/miReporteCorreoProd.html', {
                        'desde':start_date, 
                        'hasta':end_date,
                        'comp': {'name': 'INVERSIONES ANLIL 2022, C.A', 'ruc': 'J503126132', 'address': 'CALLE ESQUINA CALLE 12 CON CARRERA 19 LOCAL LOCAL COMERCIAL NRO 19 06 BARRIO BARRIO OBRERO SAN CRISTOBAL TACHIRA ZONA POSTAL 5001'},
                        'data': data,
                    })
                    mensaje.attach(MIMEText(content, 'html'))

                    mailServer.sendmail(settings.EMAIL_HOST_USER,
                                        email_to,
                                        mensaje.as_string())''' 
             
               
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de producto | almacen'
        context['entity'] = 'Reportes'
        context['list_url'] = reverse_lazy('inventaryprodstore_report')
        context['form'] = ReportForm()
        return context


class ReportProductFisicoView(Configuration, TemplateView):
    template_name = 'inventary/reportProductFisico.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_report':
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')          
                correo = request.POST.get('correo', '')   
                prod_ids = Product.objects.values_list('id', flat=True) #se puede cambiar para que se coloque el id del producto
                stock_1 = StoreProdStock.objects.filter(Q(prod_id__in=prod_ids) & Q(store_id=1)).values('prod__code','prod__name').annotate(stock1=Sum('stock_in')) 
                stock_2 = StoreProdStock.objects.filter(Q(prod_id__in=prod_ids) & Q(store_id=2)).values('prod__code','prod__name').annotate(stock2=Sum('stock_in'))
                for s in stock_1:
                    stock2=0
                    total=0
                    for s2 in stock_2:
                        if s['prod__code'] == s2['prod__code']:
                            stock2=s2['stock2']
                            total=s['stock1']+s2['stock2']
                    data.append([
                        s['prod__code'],
                        s['prod__name'],
                        '',
                        '',
                        '',                        
                    ])
                print(data)
               #almenos una venta asociada .filter(output__isnull=False)
                '''if correo:
                    print(data)
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

                    content = render_to_string('inventary/miReporteCorreoProd.html', {
                        'desde':start_date, 
                        'hasta':end_date,
                        'comp': {'name': 'INVERSIONES ANLIL 2022, C.A', 'ruc': 'J503126132', 'address': 'CALLE ESQUINA CALLE 12 CON CARRERA 19 LOCAL LOCAL COMERCIAL NRO 19 06 BARRIO BARRIO OBRERO SAN CRISTOBAL TACHIRA ZONA POSTAL 5001'},
                        'data': data,
                    })
                    mensaje.attach(MIMEText(content, 'html'))

                    mailServer.sendmail(settings.EMAIL_HOST_USER,
                                        email_to,
                                        mensaje.as_string())''' 
             
               
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Inventario | Fisico'
        context['entity'] = 'Reportes'
        context['list_url'] = reverse_lazy('inventaryprodfisico_report')
        context['form'] = ReportForm()
        return context


class ReportProductPvpView(Configuration, TemplateView):
    template_name = 'inventary/reportProductPvp.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_report':
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')          
                correo = request.POST.get('correo', '') 
                search = Product.objects.filter(Q(cate__isnull=False) | Q(cate__name__isnull=False)) #se puede cambiar para que se coloque el id del producto
                if len(start_date) and len(end_date):
                    search = search.filter(created_at__range=[start_date, end_date])
                for s in search:
                    data.append([
                        s.code,
                        s.name,
                        s.pvp,
                    ])
                print(data)
               #almenos una venta asociada .filter(output__isnull=False)
                '''if correo:
                    print(data)
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

                    content = render_to_string('inventary/miReporteCorreoProd.html', {
                        'desde':start_date, 
                        'hasta':end_date,
                        'comp': {'name': 'INVERSIONES ANLIL 2022, C.A', 'ruc': 'J503126132', 'address': 'CALLE ESQUINA CALLE 12 CON CARRERA 19 LOCAL LOCAL COMERCIAL NRO 19 06 BARRIO BARRIO OBRERO SAN CRISTOBAL TACHIRA ZONA POSTAL 5001'},
                        'data': data,
                    })
                    mensaje.attach(MIMEText(content, 'html'))

                    mailServer.sendmail(settings.EMAIL_HOST_USER,
                                        email_to,
                                        mensaje.as_string())''' 
             
               
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de producto | Precio de venta'
        context['entity'] = 'Reportes'
        context['list_url'] = reverse_lazy('inventaryprodpvp_report')
        context['form'] = ReportForm()
        return context
