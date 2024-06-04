from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy

from core.erp.mixins import Configuration, IsSuperUserMixin
from core.erp.models import Category
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from core.erp.forms import CategoryForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from core.erp.mixins import ValidatePermissionRequiredMixin


class CategoryListView(Configuration,LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Category
    template_name = 'category/list.html'
    permission_required = 'view_category'
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
                position = 1
                for i in Category.objects.all():
                    item = i.toJSON()
                    item['position'] = position
                    data.append(item)
                    position += 1
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Categorías'
        context['create_url'] = reverse_lazy('category_create')
        context['list_url'] = reverse_lazy('category_list')
        context['entity'] = 'Categorias'
        return context


class CategoryCreateView(Configuration,LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category/create.html'
    success_url = reverse_lazy('category_list')
    permission_required = 'add_category'
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
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url)
        self.object =None
        context = self.get_context_data(**kwargs)
        context['form']=form
        return  render(request, self.template_name, context)'''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Categoría'
        context['list_url'] = reverse_lazy('category_list')
        context['entity'] = 'Categorías'
        context['action'] = 'add'
        return context


class CategoryUpdateView(Configuration,LoginRequiredMixin, ValidatePermissionRequiredMixin,  UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category/create.html'
    success_url = reverse_lazy('category_list')
    permission_required = 'change_category'
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
        context['title'] = 'Edición una Categoria'
        context['entity'] = 'Categorias'
        context['list_url'] = reverse_lazy('category_list')
        context['action'] = 'edit'
        return context


class CategoryDeleteView(Configuration,LoginRequiredMixin, ValidatePermissionRequiredMixin, IsSuperUserMixin, DeleteView):
    model = Category
    template_name = 'category/delete.html'
    success_url = reverse_lazy('category_list')
    permission_required = 'delete_category'
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
        context['title'] = 'Eliminar una Categoria'
        context['entity'] = 'Categorias'
        context['list_url'] = reverse_lazy('category_list')
        return context



