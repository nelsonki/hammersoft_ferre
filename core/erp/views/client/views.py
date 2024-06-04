from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from core.erp.choices import *
from core.erp.mixins import Configuration, IsSuperUserMixin
from core.erp.models import  Client
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from core.erp.forms import ClientForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from core.erp.mixins import ValidatePermissionRequiredMixin


class ClientListView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model=Client
    template_name = 'client/list.html'
    permission_required = 'view_client'
    url_redirect = reverse_lazy('dashboard')

    @method_decorator(csrf_exempt)
    #@method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    #sobre escribir el metodo post
    def post(self, request, *args,**kwargs):
        data ={'name':'nelson'}
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Clientes'
        context['tipo_persona'] = dict(person_choices)
        context['create_url'] = reverse_lazy('client_create')
        context['list_url'] = reverse_lazy('client_list')
        context['entity'] = 'Clientes o Proveedores'
        return context


class ClientCreateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'client/create.html'
    success_url = reverse_lazy('client_list')
    permission_required = 'add_client'
    url_redirect = success_url

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
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url)
        self.object =None
        context = self.get_context_data(**kwargs)
        context['form']=form
        return  render(request, self.template_name, context)'''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Cliente|Proveedor'
        context['list_url'] = reverse_lazy('client_list')
        context['entity'] = 'Cliestes o Proveedores'
        context['action'] = 'add'
        return context


class ClientUpdateView(Configuration, LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'client/create.html'
    success_url = reverse_lazy('client_list')
    permission_required = 'change_client'
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
        context['title'] = 'Edición de Cliente'
        context['entity'] = 'Clientes o Proveedores'
        context['list_url'] = reverse_lazy('client_list')
        context['action'] = 'edit'
        return context


class ClientDeleteView(Configuration, LoginRequiredMixin, IsSuperUserMixin, ValidatePermissionRequiredMixin,  DeleteView):
    model = Client
    template_name = 'client/delete.html'
    success_url = reverse_lazy('client_list')
    permission_required = 'delete_client'
    url_redirect = success_url

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
        context['title'] = 'Eliminar un Cliente'
        context['entity'] = 'Clientes o Proveedores'
        context['list_url'] = reverse_lazy('client_list')
        return context



