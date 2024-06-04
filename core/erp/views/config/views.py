
from django.http import JsonResponse
from django.urls import reverse_lazy
from core.erp.forms import ConfigForm
from core.erp.mixins import Configuration
from core.erp.models import Config
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import   UpdateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from core.erp.mixins import ValidatePermissionRequiredMixin

class ConfigUpdateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Config
    form_class = ConfigForm
    template_name = 'config/config.html'
    success_url = reverse_lazy('dashboard')
    permission_required = 'change_config'
    url_redirect = success_url

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)
    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición Configuraciones'
        context['entity'] = 'Configuración'
        context['list_url'] = reverse_lazy('dashboard')
        context['action'] = 'edit'
        return context

