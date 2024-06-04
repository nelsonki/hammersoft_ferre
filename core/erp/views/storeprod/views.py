from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy

from core.erp.mixins import Configuration, IsSuperUserMixin
from core.erp.models import  StoreProd
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from core.erp.forms import  StoreprodForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from core.erp.mixins import ValidatePermissionRequiredMixin


class StoreprodListView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin,  ListView):
    model=StoreProd
    template_name = 'storeprod/list.html'
    permission_required = 'view_storeprod'
    url_redirect= reverse_lazy('dashboard')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    #sobre escribir el metodo post
    def post(self, request, *args,**kwargs):
        data ={'name':'nelson'}
        return JsonResponse(data)
    
    def count_store(self):
        count = StoreProd.objects.count()
        return count

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Almacenes'
        context['create_url'] = reverse_lazy('storeprod_create')
        context['list_url'] = reverse_lazy('storeprod_list')
        context['entity'] = 'Alamcenes'
        context['count_store'] = self.count_store()
        return context


class StoreprodCreateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = StoreProd
    form_class = StoreprodForm
    template_name = 'storeprod/create.html'
    success_url = reverse_lazy('storeprod_list')
    permission_required = 'add_storeprod'
    url_redirect = success_url

    #@method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    '''def post(self, request, *args, **kwargs):
        form = StoreprodForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url)
        self.object =None
        context = self.get_context_data(**kwargs)
        context['form']=form
        return  render(request, self.template_name, context)'''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Alamcen'
        context['list_url'] = reverse_lazy('storeprod_list')
        context['entity'] = 'Almacenes'
        context['action'] = 'add'
        return context


class StoreprodUpdateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = StoreProd
    form_class = StoreprodForm
    template_name = 'storeprod/create.html'
    success_url = reverse_lazy('storeprod_list')
    permission_required = 'change_storeprod'
    url_redirect = success_url

    #@method_decorator(login_required)
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
        context['title'] = 'Edición una Almacen'
        context['entity'] = 'Almacenes'
        context['list_url'] = reverse_lazy('storeprod_list')
        context['action'] = 'edit'
        return context


class StoreprodDeleteView(Configuration, LoginRequiredMixin, IsSuperUserMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = StoreProd
    template_name = 'storeprod/delete.html'
    success_url = reverse_lazy('storeprod')
    permission_required = 'delete_storeprod'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    #@method_decorator(login_required)
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
        context['title'] = 'Eliminar una Almacen'
        context['entity'] = 'Almacenes'
        context['list_url'] = reverse_lazy('storeprod_list')
        return context



