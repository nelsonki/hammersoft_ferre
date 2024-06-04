from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from core.erp.mixins import Configuration
 
from core.erp.models import Input
from core.reports.forms import ReportForm

from django.db.models.functions import Coalesce
from django.db.models import Sum
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import uuid


from django.http import  JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
class ReportInputView(Configuration, TemplateView):
    template_name = 'input/report.html'

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
                search = Input.objects.all()
                if len(start_date) and len(end_date):
                    search = search.filter(date_joined__range=[start_date, end_date])
                for s in search:
                    tipo = "Factura" if s.tipoFacNot == '1' else "tipoFacNot" if s.tipoFacNot == '2' else "Nota de Entrega"
                    data.append([
                        s.id,
                        s.num_liquidacion,
                        tipo,
                        s.cli.name,
                        s.date_joined.strftime('%Y-%m-%d %H:%M'),
                        format(s.subtotal, '.2f'),
                        format(s.tax, '.2f'),
                        format(s.total, '.2f'),
                    ])
                print(data)
                subtotal = search.aggregate(subtotal=Sum('subtotal')).get('subtotal') or 0
                tax = search.aggregate(tax=Sum('tax')).get('tax') or 0
                total = search.aggregate(total=Sum('total')).get('total') or 0

                data.append([
                    '---',
                    '---',
                    '---',
                    '---',
                    '---',
                    format(subtotal, '.2f'),
                    format(tax, '.2f'),
                    format(total, '.2f'),
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

                    content = render_to_string('input/miReporteCorreo.html', {
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Entradas'
        context['entity'] = 'Reportes'
        context['list_url'] = reverse_lazy('input_report')
        context['form'] = ReportForm()
        return context

