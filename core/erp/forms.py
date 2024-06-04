from django.forms import *

from core.erp.models import *
from datetime import datetime

import pytz

class CategoryForm(ModelForm):

    class Meta:
        model = Category
        fields = '__all__'
        labels= {
           'name': 'Nombre',
            'description': 'Descripción',
            'image': 'Imagen',
        }
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Nombre',
                'autocomplete': 'off'
            }),
            'description': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Descripción',
                'autocomplete': 'off'

            }),


        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class StoreprodForm(ModelForm):

    class Meta:
        model = StoreProd
        fields = '__all__'
        labels= {
           'name': 'Nombre',

        }
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Nombre',
                'autocomplete': 'off'
            }),



        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ClientForm(ModelForm):

    class Meta:
        model = Client
        fields = '__all__'
        labels= {
           'name': 'Nombre|Registro',
            'lastname': 'Apellido',
            'dni':'Documento',
            'gender':'Sexo',
            'phone':'Teléfono',
            'address':'Dirección',
            'company':'Compañia',
            'email':'Correo Electronico',
            'kind':'Tipo de persona',
            'image': 'Imagen',
        }
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Nombre',
                'autocomplete': 'off'
            }),
            'lastname': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Apellido',
                'autocomplete': 'off'

            }),
            'dni': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Dni',
                'autocomplete': 'off'

            }),
            'phone': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Teléfono',
                'autocomplete': 'off'

            }),
            'address': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Dirección',
                'autocomplete': 'off'

            }),
            'company': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Compañia',
                'autocomplete': 'off'

            }),
            'email': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Correo',
                'autocomplete': 'off'

            }),
            'kind': Select(attrs={'class': 'form-control'}),

            'gender': Select(attrs={'class': 'form-control'}),

        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                instance = form.save()
                data = instance.toJSON()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ProductForm(ModelForm):

    class Meta:
        model = Product
        fields = '__all__'
        labels = {
           'code': 'Código del producto',
            'name': 'Nombre del producto',
            'reference': 'Nombre referencial',
            'cate': 'Categoría',
            'store': 'Almacen',
            'image': 'Imagen del producto',
            'pvp': 'Precio de venta (PVP)',
            'pvp2': 'Precio de venta (PVP) opcional',
            'pvp3': 'Precio de combo',
            'price_in':'Costo Actual',
            'codbar': 'Código de barra',
            'classPro': 'Clase de licor',
            'lt': 'Litros',
            'capacity': 'Capacidad de llenado',
            'tradinghouse': 'Casa Comercial',
            'is_active': 'Estado del producto',
            'is_combo': 'Producto tipo combo',

        }
        widgets = {
            'code': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Código',
                'autocomplete': 'off'
            }),
            'name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Nombre',
                'autocomplete': 'off'
            }),
            'reference': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar referencia',
                'autocomplete': 'off'

            }),
            'cate': Select(attrs={'class': 'form-control'}),
            'store': SelectMultiple(attrs={
                'class': 'form-control select2',  
                'id':'store', 
                 'multiple': 'multiple',
             }),

            'pvp': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar PVP',
                'autocomplete': 'off',
                'id':'pvp'


            }),
            'pvp2': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar PVP opcional',
                'autocomplete': 'off',
                'id':'pvp2'

            }),
            'pvp3': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar PVP combo',
                'autocomplete': 'off',
                'id':'pvp3'
            }),
            
            'stock_min': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Existencia minima',
                'autocomplete': 'off',
                'id':'stock_min'
            }),
            'price_in': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Costo Actual',
                'autocomplete': 'off',
                'readonly': True,

            }),
            'codbar': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Código de barra',
                'autocomplete': 'off'

            }),
            'classPro': Select(attrs={'class': 'form-control'}),

            'lt': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Litros',
                'autocomplete': 'off'

            }),
            'capacity': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Capacidad de llenado',
                'autocomplete': 'off'

            }),
            'tradinghouse': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar Nombre',
                'autocomplete': 'off'
            }),
            'is_active': Select(attrs={'class': 'form-control'}),
            'is_combo': CheckboxInput(
                attrs={
                    'class':'form-control custom-control-input',
                    'id':'customSwitch1'
                    }

                ),

        }
   

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class ProComboForm(ModelForm):

        
    class Meta:
        model = ProdCombo
        fields = '__all__'
        widgets = {

            'store': Select(attrs={
                'name':'store',
                'class': 'form-control select2',
             }),
            'prod': Select(attrs={
                'class': 'form-control select2',
                'name':'prod'
            }),
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
          'subtotal': TextInput(attrs={
                'readonly': True,
                'class': 'form-control ',
                'style':'text-align:end; font-size: 30px; font-weight: bold; height:60px; color: green;'
            }),
           
        }

class OutputForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cli'].queryset = Client.objects.none()
        
    class Meta:
        tz = pytz.timezone('America/Caracas')
        model = Output
        fields = '__all__'
        widgets = {
            'date_joined': DateTimeInput(
                attrs={                    
                    'value': datetime.now(tz).strftime('%Y-%m-%d %H:%M'),
                    'autocomplete': 'off',
                    'class': 'form-control  ',
                 
                }
            ),
            'store': Select(attrs={
                'name':'store',
                'class': 'form-control select2',
             }),
            'cli': Select(attrs={
                'class': 'form-control select2',
             }),

            'tax': TextInput(attrs={
                'class': 'form-control',
                'style':'text-align:end'
            }),
            'subtotal': TextInput(attrs={
                'readonly': True,
                'class': 'form-control ',
                'style':'text-align:end'
            }),
            'total': TextInput(attrs={
                'readonly': True,
                'class': 'form-control  ',
                'style':'text-align:end; font-size: 30px; font-weight: bold; height:60px; color: green;'
            }),
            'peso': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
                'style':'text-align:end'
            }),
            'bolivar': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
                'style':'text-align:end'
            }),
           
        }

class InputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cli'].queryset = Client.objects.none()
        
    class Meta:
        tz = pytz.timezone('America/Caracas')
        model = Input
        fields = '__all__'
        widgets = {
            'date_joined': DateTimeInput(
                attrs={
                    'value': datetime.now(tz).strftime('%Y-%m-%d %H:%M'),
                    'autocomplete': 'off',
                    'class': 'form-control  ',
                 
                }
            ),
            'date_reminder': DateTimeInput(
                attrs={
                    'value': datetime.now(tz).strftime('%Y-%m-%d %H:%M'),
                    'autocomplete': 'off',
                    'class': 'form-control ',
                    'id':'date_reminder'
                }
            ),
            'status': Select(
                attrs={
                    'class': 'form-control',
                    'id':'status'
                    }
                    ),             

            'store': Select(attrs={
                'name':'store',
                'class': 'form-control select2',
             }),
            'tipoFacNot': Select(attrs={'class': 'form-control'}),             
            'cli': Select(attrs={
                'class': 'form-control select2',
             }),
             'num_liquidacion': TextInput(attrs={
                'name':'num_liquidacion',
                'class': 'form-control',
            }),
            'tax': TextInput(attrs={
                'class': 'form-control',
                'style':'text-align:end'

            }),
            'subtotal': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
                'style':'text-align:end'

            }),
            'total': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
                'style':'text-align:end; font-size: 30px; font-weight: bold; height:60px; color: green;'

            })
        }

class MovementForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    class Meta:
        tz = pytz.timezone('America/Caracas')
        model = Movement
        fields = '__all__'
        widgets = {
            'description': TextInput(attrs={
                'class': 'form-control',
            }),
            'date_joined': DateTimeInput(
                attrs={
                    'value': datetime.now(tz).strftime('%Y-%m-%d %H:%M'),
                    'autocomplete': 'off',
                    'class': 'form-control  ',
                 
                }
            ),
            'in_store': Select(attrs={
                'name':'in_store',
                'class': 'form-control select2',
             }),
             'out_store': Select(attrs={
                'name':'out_store',
                'class': 'form-control select2',
             }),
             
             
        }

class OrderForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cli'].queryset = Client.objects.none()
        
    class Meta:
        tz = pytz.timezone('America/Caracas')
        model = Order
        fields = '__all__'
        widgets = {
            'date_joined': DateTimeInput(
                attrs={
                    'value': datetime.now(tz).strftime('%Y-%m-%d %H:%M'),
                    'autocomplete': 'off',
                    'class': 'form-control  ',
                 
                }
            ),
            'store': Select(attrs={
                'name':'store',
                'class': 'form-control select2',
             }),
            'cli': Select(attrs={
                'class': 'form-control select2',
             }),
             
            'tax': TextInput(attrs={
                'class': 'form-control',
                'style':'text-align:end'

            }),
            'subtotal': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
                'style':'text-align:end'

            }),
            'total': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
                'style':'text-align:end; font-size: 30px; font-weight: bold; height:60px; color: green;'

            }),
            'peso': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
                'style':'text-align:end'
            }),
            'bolivar': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
                'style':'text-align:end'
            }),
        }

class ConfigForm(ModelForm):

    class Meta:
        model = Config
        fields = '__all__'
        labels= {
            'cambioVentaDolarBs': 'Cambio dolar a Bolivar',
            'cambioVentaDolarCop': 'Cambio dolar a pesos',
        }
        widgets = {
            'cambioVentaDolarBs': TextInput(attrs={
                'class': 'form-control',
            }),

            'cambioVentaDolarCop': TextInput(attrs={
                'class': 'form-control',
            }),

        }

 

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ClosingForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    class Meta:
        tz = pytz.timezone('America/Caracas')
        model = Closing
        fields = '__all__'

        widgets = {
   
             'observation': TextInput(attrs={
                'class': 'form-control',
            }),
            'total': TextInput(attrs={
                'readonly': True,
                'class': 'form-control  ',
                'style':'text-align:end; font-size: 30px; font-weight: bold; height:60px; color: green;',
                'name':'total'
            }),
            'dolar': TextInput(attrs={
                'class': 'form-control',
                'style':'text-align:end'
            }),
            'peso': TextInput(attrs={
                'class': 'form-control',
                'style':'text-align:end'
            }),
            'bolivar': TextInput(attrs={
                'class': 'form-control',
                'style':'text-align:end'
            }),
           
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                instance = form.save()
                data = instance.toJSON()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data
    
class AdjustmentForm(ModelForm):
        
    class Meta:
        tz = pytz.timezone('America/Caracas')
        model = Adjustment
        fields = '__all__'
        widgets = {
            'date_joined': DateTimeInput(
                attrs={                    
                    'value': datetime.now(tz).strftime('%Y-%m-%d %H:%M'),
                    'autocomplete': 'off',
                    'class': 'form-control  ',
                 
                }
            ),
            'store': Select(attrs={
                'name':'store',
                'class': 'form-control select2',
             }),
            'observation': TextInput(attrs={
                'class': 'form-control',
                'name':'observation',

            }),

           
        }