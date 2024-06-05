from datetime import datetime
from itertools import product

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from core.erp.mixins import Configuration
from django.db.models import Q

from core.erp.models import Config, Output, Input, Product, DetOutput, StoreProdStock
from core.user.models import User

 
class DashboardView(Configuration,TemplateView):
    template_name = 'dashboard.html'

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
                    'name': 'Porcentaje de venta',
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
            elif action == 'searchdataDash':
                data = []
                for i in Output.objects.all().order_by('-date_joined')[:5]:
                    data.append(i.toJSON())
           
            elif action == 'search_details_prodDash':
                data = []
                for i in DetOutput.objects.filter(output_id=request.POST['id']):
                    data.append(i.toJSON())
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
    

    
    def year(self):
        year = datetime.now().year
        return year
    
    def month(self):
        month = datetime.now().month
        return month
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = self.year()
        context['month'] = self.month()
        context['panel'] = 'Panel del administrador'
        context['get_graph_output_year_month'] = self.get_graph_output_year_month()
        context['get_graph_output_products_year_month'] = self.get_graph_output_products_year_month()

        return context

