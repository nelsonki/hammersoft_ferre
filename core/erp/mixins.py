from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from core.erp.models import Config, Output, Product, StoreProdStock, Input
from core.user.models import User
from crum import get_current_request
from django.db.models import Sum
from datetime import datetime
import pytz
from django.db.models import Q

class Configuration(object):#las configuraciones principales del sistema, la moneda, nombre de la empres, entre otras variables
    def configuration(self):
        count = Config.objects.first()
        if count:
            return count.id
    
    def datosConfig(object):
        items = Config.objects.all()
        data = []
        for item in items:
            data.append(item)
        print(data)
        return data

    def product_cost_pvp(self):
        count_cost_pvp =0
        for g in Product.objects.filter(Q(cate__isnull=False) | Q(cate__name__isnull=False)):
            if(g.price_in > g.pvp):
                count_cost_pvp +=1  
        return count_cost_pvp

    def product_stock_min_count(self):
        count_stock_min =0
        for g in Product.objects.filter(Q(cate__isnull=False) | Q(cate__name__isnull=False)):
            prod_stock_min = g.stock_min
            product_stock_general = StoreProdStock.objects.filter(prod_id=g.id).aggregate(stock_in=Sum('stock_in')).get('stock_in') or 0 
            if(prod_stock_min > product_stock_general):
                count_stock_min +=1  
        return count_stock_min
    
    def input_time_alert(self):
        tz = pytz.timezone('America/Caracas')
        fechaActual = datetime.now(tz)
        count_time_alert =0
        for g in Input.objects.all():
            default_date = None
            fechaRecordatorio = g.date_reminder if g.date_reminder else default_date
            if fechaRecordatorio and fechaActual > fechaRecordatorio and g.status =='0':
                count_time_alert +=1  
        return count_time_alert

    def product_count(self):
        product_count = Product.objects.count()
        return product_count
    
    def output_count(self):
        output_count = Output.objects.count()
        return output_count
    
    def input_count(self):
        input_count = Input.objects.count()
        return input_count
    
    def user_count(self):
        user_count = User.objects.count()
        return user_count



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alert_stock_mim'] = self.product_stock_min_count()
        context['input_time_alert'] = self.input_time_alert()
        context['cantProd'] = self.product_count()
        context['alert_cost_pvp'] = self.product_cost_pvp()
        context['cantOutput'] = self.output_count()
        context['cantInput'] = self.input_count()
        context['cantUser'] = self.user_count()
        context['config'] = self.configuration()
        context['dataConfig'] = self.datosConfig() 
        return context

class IsSuperUserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, 'No tiene permisos para ingresar a este modulo')
        return redirect('dashboard')

class ValidatePermissionRequiredMixin(object):
    permission_required = ''
    url_redirect = None

    # def get_perms(self):
    #     if isinstance(self.permission_required, str):
    #         perms = (self.permission_required,)
    #     else:
    #         perms = self.permission_required
    #     return perms

    def get_url_redirect(self):
        if self.url_redirect is None:
            return redirect('dashboard')
        return self.url_redirect

    def dispatch(self, request, *args, **kwargs):
        request = get_current_request()
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if 'group' in request.session:
            group = request.session['group']
            #group = Group.objects.get(pk=1)
            if group.permissions.filter(codename=self.permission_required):
                return super().dispatch(request, *args, **kwargs)
        messages.error(request, 'No tiene permiso para ingresar a este módulo')
        return HttpResponseRedirect(self.get_url_redirect())


# class ValidatePermissionRequiredMixin(object):
#     permission_required = ''
#     url_redirect = None
#
#     def get_perms(self):
#         if isinstance(self.permission_required, str):
#             perms = (self.permission_required,)
#         else:
#             perms = self.permission_required
#         return perms
#
#     def get_url_redirect(self):
#         if self.url_redirect is None:
#             return reverse_lazy('index')
#         return self.url_redirect
#
#     def dispatch(self, request, *args, **kwargs):
#         if request.user.has_perms(self.get_perms()):
#             return super().dispatch(request, *args, **kwargs)
#         messages.error(request, 'No tiene permiso para ingresar a este módulo')
#         return HttpResponseRedirect(self.get_url_redirect())
