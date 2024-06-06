from django.db import models
from datetime import datetime, timezone
from datetime import datetime
import numpy as np

from django.forms import model_to_dict
from django.db.models import Q
from django.db import transaction

# Create your models here.
from core.erp.choices import *
from app.settings import MEDIA_URL, STATIC_URL
from core.models import BaseModel

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

#ALMACEN DE LOS PRODUCTOS
class StoreProd(models.Model):
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

 
    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def toJSON(self):
        item = model_to_dict(self)
        return item
    
    class Meta:
        verbose_name = 'Almacen'
        verbose_name_plural = 'Almacenes'
        ordering = ['id']



#CATEGORIA DE LOS PRODUCTOS
class Category(BaseModel):
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    image = models.ImageField(upload_to='category/%Y/%m/%d', null=True, blank=True)
    description = models.CharField(max_length=150, verbose_name='Descripción', null=True, blank=True)
    is_delete = models.IntegerField(default=0, null=True, blank=True)
    delete_at = models.DateTimeField(default=datetime.now)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return '{}'.format(self.name)

    def toJSON(self):
        item = model_to_dict(self)
        item['image'] = self.get_image()

        return item

    def get_image(self):
        if self.image:
            return '{}{}'.format(MEDIA_URL, self.image)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['id']


#PRODUCTO
class Product(models.Model):
    store = models.ManyToManyField(StoreProd, through='StoreProdStock')
    cate = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    code = models.CharField(max_length=6, verbose_name='Código')
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True )
    stock = models.IntegerField(default=0, verbose_name='Cantidad', null=True, blank=True)
    stock_min = models.IntegerField(default=0, verbose_name='Existencia minima', null=True, blank=True)
    image = models.ImageField(upload_to='product/%Y/%m/%d', null=True, blank=True)
    price_in = models.DecimalField(default=0, max_digits=9, decimal_places=4, verbose_name='Precio de compra', null=True, blank=True)
    pvp = models.DecimalField(default=0, max_digits=9, decimal_places=2, verbose_name='Precio de venta 1', null=True, blank=True)
    pvp2 = models.DecimalField(default=0, max_digits=9, decimal_places=2, verbose_name='Precio de venta 2', null=True, blank=True)
    pvp3 = models.DecimalField(default=0, max_digits=9, decimal_places=2,  verbose_name='Precio de combo', null=True, blank=True)
    unit = models.IntegerField(default=0, verbose_name='Unidad', null=True, blank=True)
    classPro = models.CharField(max_length=100, choices=licor_choices, default='pvp', verbose_name='Tipo de licor')
    codbar = models.CharField(max_length=50, verbose_name='Codigo de barra', null=True, blank=True)
    lt = models.CharField(max_length=50, verbose_name='Litros', null=True, blank=True)
    capacity = models.CharField(max_length=50, verbose_name='Capacidad', null=True, blank=True)
    is_active = models.CharField(max_length=10, choices=status_choices, default='1', verbose_name='Estatus')
    tradinghouse =models.CharField(max_length=150, verbose_name='Casa Comercial', null=True, blank=True )
    is_combo =models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        item['cate'] = self.cate.toJSON()
        item['store'] =  [{'id': g.id, 'name': g.name} for g in self.store.all()]
        item['image'] = self.get_image()
        item['pvp'] = format(self.pvp, '.2f')
        item['pvp2'] = format(self.pvp2, '.2f')
        item['pvp3'] = format(self.pvp3, '.2f')
        item['price_in'] = format(self.price_in, '.4f')
        return item

    def get_image(self):
        if self.image:
            return '{}{}'.format(MEDIA_URL, self.image)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['id']

#PRODUCTO COMBO
class ProdCombo(models.Model):
    name = models.CharField(max_length=100, unique=True)
    prod = models.OneToOneField(Product, on_delete=models.SET_NULL, null=True, blank=True)
    store = models.ForeignKey(StoreProd, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2,  verbose_name='Precio del combo', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)


    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['store'])
        item['prod'] = self.prod.toJSON()
        item['subtotal'] = format(self.subtotal, '.2f')

        return item
    
    def natural_key(self):
        return (self.name,)

    class Meta:
        verbose_name = 'Combo de productos'
        verbose_name_plural = 'Combo de productos'
        ordering = ['id']


class DetProdCombo(models.Model):
    prodcombo = models.ForeignKey(ProdCombo, on_delete=models.SET_NULL, null=True, blank=True)
    prod = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    unit = models.IntegerField(default=0)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)
    
    def __str__(self):
        return self.prod.name
    
    def toJSON(self):
            item = model_to_dict(self, exclude=['prodcombo'])
            item['prod'] = self.prod.toJSON()
            return item

    class Meta:
        verbose_name = 'Detalle de Salida'
        verbose_name_plural = 'Detalle de Salidas'
        ordering = ['id']

#ALMACEN DE LOS PRODUCTOS y el stock
class StoreProdStock(models.Model):
    prod = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    store = models.ForeignKey(StoreProd, on_delete=models.SET_NULL, null=True, blank=True)
    stock_in = models.IntegerField(default=0, verbose_name='Cantidad', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

 
    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    class Meta:
        verbose_name = 'Almacen Producto stock'
        verbose_name_plural = 'Almacenes Producto stock'
        ordering = ['id']


#CLIENTE o PROVEEDOR
class Client(models.Model):
    name = models.CharField(max_length=150, verbose_name='Nombres', null=True, blank=True )
    lastname = models.CharField(max_length=150, verbose_name='Apellidos', null=True, blank=True)
    dni = models.CharField(max_length=10, unique=True, verbose_name='Dni')
    gender = models.CharField(max_length=10, choices=gender_choices, default='M', verbose_name='Sexo')
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    company = models.CharField(max_length=150, verbose_name='Compañia', null=True, blank=True)
    image = models.ImageField(upload_to='product/%Y/%m/%d', null=True, blank=True)
    email= models.CharField(max_length=50, null=True, blank=True)
    kind= models.CharField(max_length=20, choices=person_choices, default='1', verbose_name='Tipo de Persona')
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
            return '{} {} / {}'.format(self.name, self.lastname, self.dni)

    def toJSON(self):
        item = model_to_dict(self)
        item['gender'] = {'id': self.gender, 'name': self.get_gender_display()}
        #item['date_birthday'] = self.date_birthday.strftime('%Y-%m-%d')
        item['image'] = self.get_image()
        item['kind'] = {'id': self.kind, 'name': self.get_kind_display()}
        item['full_name'] = self.get_full_name()

        return item

    def get_image(self):
        if self.image:
            return '{}{}'.format(MEDIA_URL, self.image)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['id']

#SALIDA
class Output(models.Model):
    cli = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    store = models.ForeignKey(StoreProd, on_delete=models.SET_NULL, null=True, blank=True)
    date_joined = models.DateTimeField(default=datetime.now)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    tax = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    peso = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    bolivar = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    totalDivisa =  models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    status =models.CharField(max_length=10, choices=cierre_choices, default='0', verbose_name='Cierre')
    is_active= models.CharField(max_length=10, choices=status_choices, default='1', verbose_name='Estatus')
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return getattr(self.cli, 'name', 'N/A')
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['store'])
        item['cli'] = getattr(self.cli, 'name', 'N/A')
        item['subtotal'] = format(self.subtotal, '.2f')
        item['tax'] = format(self.tax, '.2f')
        item['totalDivisa'] = format(self.totalDivisa, '.2f')
        item['total'] = format(self.total, '.2f')
        item['peso'] = format(self.peso, '.2f')
        item['bolivar'] = format(self.bolivar, '.2f')
        item['status'] = {'id': self.status, 'name': self.get_status_display()}
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d %H:%M') 
        return item

    def delete(self, using=None, keep_parents=False):
        with transaction.atomic():          
            Inventory.objects.filter(operaOut_id=self).all().delete()
            for det in self.detoutput_set.all():
                if  Product.objects.filter(Q(id=det.prod_id ) & Q(is_combo=1)):
                    prodcombo = ProdCombo.objects.filter(prod_id=det.prod_id )
                    for p in prodcombo:
                        item = p.toJSON()
                        for j in DetProdCombo.objects.filter(prodcombo_id=item['id']):
                            itemj = j.toJSON()
                            print(itemj['prod']['id'])
                            storeProdStock = StoreProdStock.objects.get(store__in=[self.store_id], prod__in=[itemj['prod']['id']])
                            storeProdStock.stock_in += (itemj['amount'] * det.amount)
                            storeProdStock.save()
                            det.prod.stock += (itemj['amount'] * det.amount)
                            det.save()
                else:    
                    storeProdStock = StoreProdStock.objects.get(store__in=[self.store_id], prod__in=[det.prod_id ])
                    storeProdStock.stock_in += det.amount
                    storeProdStock.save()
                    det.prod.stock += det.amount
                    det.prod.save()
                    print('otro producto')
            super(Output, self).delete()                  
    class Meta:
        verbose_name = 'Salida'
        verbose_name_plural = 'Salidas'
        ordering = ['id']

#DETALLE DE SALIDA
class DetOutput(models.Model):
    output = models.ForeignKey(Output, on_delete=models.SET_NULL, null=True, blank=True)
    prod = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    amount = models.IntegerField(default=0)
    unit = models.IntegerField(default=0)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.prod.name
    
    def toJSON(self):
            item = model_to_dict(self, exclude=['output'])
            item['prod'] = self.prod.toJSON()
            item['price'] = format(self.price, '.2f')
            item['subtotal'] = format(self.subtotal, '.2f')
            return item

    class Meta:
        verbose_name = 'Detalle de Salida'
        verbose_name_plural = 'Detalle de Salidas'
        ordering = ['id']

#ORDEN DE SALIDA
class Order(models.Model):
    cli = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)  
    store = models.ForeignKey(StoreProd, on_delete=models.SET_NULL, null=True, blank=True)
    date_joined = models.DateTimeField(default=datetime.now)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    tax = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    peso = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    bolivar = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    totalDivisa =  models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    is_active= models.CharField(max_length=10, choices=status_choices, default='1', verbose_name='Estatus')
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return getattr(self.cli, 'name', 'N/A')
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['store'])
        item['cli'] = getattr(self.cli, 'name', 'N/A')
        item['subtotal'] = format(self.subtotal, '.2f')
        item['tax'] = format(self.tax, '.2f')
        item['totalDivisa'] = format(self.totalDivisa, '.2f')
        item['total'] = format(self.total, '.2f')
        item['peso'] = format(self.peso, '.2f')
        item['bolivar'] = format(self.bolivar, '.2f')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d %H:%M') 
        print(item)
        return item
    
    class Meta:
        verbose_name = 'Orden de Salida'
        verbose_name_plural = 'Orden de Salida'
        ordering = ['id']

#DETALLE DE ORDEN DE SALIDA
class DetOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    prod = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    amount = models.IntegerField(default=0)
    unit = models.IntegerField(default=0)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.prod.name
    
    def toJSON(self):
            item = model_to_dict(self, exclude=['order'])
            item['prod'] = self.prod.toJSON()
            item['price'] = format(self.price, '.2f')
            item['subtotal'] = format(self.subtotal, '.2f')
            return item

    class Meta:
        verbose_name = 'Detalle de Orden'
        verbose_name_plural = 'Detalle de Ordenes'
        ordering = ['id']


#ENTRADA
class Input(models.Model):
    num_liquidacion =  models.CharField(max_length=20)
    store = models.ForeignKey(StoreProd, on_delete=models.SET_NULL, null=True, blank=True)
    cli = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    date_joined = models.DateTimeField(default=datetime.now)
    date_reminder = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de recordatorio')
    date_pay = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de cancelado')

    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    tax = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    totalDivisa =  models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    status =models.CharField(max_length=10, choices=pago_choices, default='0', verbose_name='Estatus')
    tipoFacNot = models.CharField(max_length=10, choices=fact_choices, default='1', verbose_name='Tipo de Factura')
    is_active= models.CharField(max_length=10, choices=status_choices, default='1', verbose_name='Estatus')
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return getattr(self.cli, 'name', 'N/A')
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['store'])
        item['cli'] = getattr(self.cli, 'name', 'N/A')
        item['tipoFacNot'] = {'id': self.tipoFacNot, 'name': self.get_tipoFacNot_display()}
        item['subtotal'] = format(self.subtotal, '.2f')
        item['tax'] = format(self.tax, '.2f')
        item['totalDivisa'] = format(self.totalDivisa, '.2f')
        item['total'] = format(self.total, '.2f')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d %H:%M') 
       # default_date = '0000-00-00 00:00'
        default_date = ''
        item['date_reminder'] = self.date_reminder.strftime('%Y-%m-%d %H:%M') if self.date_reminder else default_date
        item['date_pay'] = self.date_pay.strftime('%Y-%m-%d %H:%M') if self.date_pay else default_date
        item['status'] = {'id': self.status, 'name': self.get_status_display()}


        print(item)
        return item

    def delete(self, using=None, keep_parents=False):
        with transaction.atomic():          
            Inventory.objects.filter(operaIn_id=self).all().delete()
            for det in self.detinput_set.all():   
                storeProdStock = StoreProdStock.objects.get(store__in=[1], prod__in=[det.prod_id ])
                storeProdStock.stock_in -= det.amount
                storeProdStock.save()
                det.prod.stock -= det.amount
                det.prod.save()
            super(Input, self).delete()  

    class Meta:
        verbose_name = 'Entradas'
        verbose_name_plural = 'Entradas'
        ordering = ['id']

#DETALLE DE ENTRADAS
class DetInput(models.Model):
    input = models.ForeignKey(Input, on_delete=models.SET_NULL, null=True, blank=True)
    prod = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    costBs = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    rate = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    cost = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    amount = models.IntegerField(default=0)
    unit = models.IntegerField(default=0)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.prod.name
    
    def toJSON(self):
            item = model_to_dict(self, exclude=['input'])
            item['prod'] = self.prod.toJSON()
            item['costBs'] = format(self.costBs, '.2f')
            item['rate'] = format(self.rate, '.2f')
            item['cost'] = format(self.cost, '.4f')
            item['subtotal'] = format(self.subtotal, '.2f')
            return item

    class Meta:
        verbose_name = 'Detalle de Entrada'
        verbose_name_plural = 'Detalle de Entradas'
        ordering = ['id']


#MOVIMIENTO
class Movement(models.Model):    
    description =  models.CharField(max_length=200)
    date_joined = models.DateTimeField(default=datetime.now)
    is_active= models.CharField(max_length=10, choices=status_choices, default='1', verbose_name='Estatus')
    in_store=models.ForeignKey(StoreProd,   on_delete=models.SET_NULL, null=True, blank=True, related_name='storeprod_in_store')
    out_store=models.ForeignKey(StoreProd,   on_delete=models.SET_NULL, null=True, blank=True, related_name='storeprod_out_store')
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return 'Descripción del movimiento: {}'.format(self.description)
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['storeprod_in_store','storeprod_out_store'])
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d %H:%M') 
        item['in_store'] = self.in_store.toJSON()
        item['out_store'] = self.out_store.toJSON()
        print(item)
        return item

    def delete(self, using=None, keep_parents=False):
        Inventory.objects.filter(operaMov_id=self).all().delete()
        for det in self.detmov_set.all():
            det.prod.stock -= det.amount #hay que modificar esto
            det.prod.save()
        super(Input, self).delete()

    def delete(self, using=None, keep_parents=False):
        Inventory.objects.filter(operaMove_id=self).all().delete()
        for det in self.detmov_set.all():
            det.prod.stock += det.amount
            det.prod.save()
            storeProdStock = StoreProdStock.objects.get(store__in=[self.in_store_id], prod__in=[det.prod_id])
            storeProdStock.stock_in += det.amount
            storeProdStock.save()
            storeProdStock = StoreProdStock.objects.get(store__in=[self.out_store_id], prod__in=[det.prod_id])
            storeProdStock.stock_in -= det.amount
            storeProdStock.save()
        super(Movement, self).delete()

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering = ['id'] 

 
#DETALLE DE MOVIMIENTO
class DetMov(models.Model):
    movement = models.ForeignKey(Movement, on_delete=models.SET_NULL, null=True, blank=True)
    prod = models.ForeignKey(Product,  on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)
    
    def __str__(self):
        return self.mov.name
    
    def toJSON(self):
            item = model_to_dict(self, exclude=['movement'])
            item['prod'] = self.prod.toJSON()
            return item

    class Meta:
        verbose_name = 'Detalle de Movimiento'
        verbose_name_plural = 'Detalle de Movimientos'
        ordering = ['id']


#AJUSTE DE INVENTARIO
class Adjustment(models.Model):
    store = models.ForeignKey(StoreProd, on_delete=models.SET_NULL, null=True, blank=True)
    date_joined = models.DateTimeField(default=datetime.now)
    observation = models.CharField(max_length=200, verbose_name='Observaciones generales')
    is_active= models.CharField(max_length=10, choices=status_choices, default='1', verbose_name='Estatus')
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.store.name
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['store'])
        item['store'] = self.store.toJSON()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d %H:%M') 
        return item

    def delete(self, using=None, keep_parents=False):
        with transaction.atomic():          
            Inventory.objects.filter(operaAdjustment_id=self).all().delete()
            for det in self.detadjustment_set.all(): 
                    storeProdStock = StoreProdStock.objects.get(store__in=[self.store_id], prod__in=[det.prod_id ])
                    if det.types==0:
                            storeProdStock.stock_in -= det.amount
                            storeProdStock.save()
                            det.prod.stock -= det.amount
                            det.prod.save()
                    else:
                            storeProdStock.stock_in += det.amount
                            storeProdStock.save()
                            det.prod.stock += det.amount
                            det.prod.save()
            super(Adjustment, self).delete()                 
    class Meta:
        verbose_name = 'Adjuste'
        verbose_name_plural = 'Adjuste'
        ordering = ['id']

#DETALLE DE AJUSTE DE INVENTARIO
class DetAdjustment(models.Model):
    adjustment = models.ForeignKey(Adjustment, on_delete=models.SET_NULL, null=True, blank=True)    
    prod = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    types= models.CharField(max_length=10, choices=adjust_choices, default='0', verbose_name='Estatus de adjuste')
    stock_previous =models.IntegerField(default=0)
    store1_previous = models.IntegerField(default=0)
    store2_previous = models.IntegerField(default=0)

    amount =models.IntegerField(default=0)

    stock_next =models.IntegerField(default=0)
    store1_next = models.IntegerField(default=0)
    store2_next = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.prod.name
    
    def toJSON(self):
            item = model_to_dict(self, exclude=['adjustment'])
            item['prod'] = self.prod.toJSON()
            item['types'] = {'id': self.types, 'name': self.get_types_display()}
            return item

    class Meta:
        verbose_name = 'Detalle del ajuste'
        verbose_name_plural = 'Detalle de Ajuste de Inventario'
        ordering = ['id']

class Inventory(models.Model):
    prod = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    in_store=models.ForeignKey(StoreProd,   on_delete=models.SET_NULL, null=True, blank=True,related_name='storeinv_in_store')
    out_store=models.ForeignKey(StoreProd,   on_delete=models.SET_NULL, null=True, blank=True,related_name='storeinv_out_store')
    stock = models.IntegerField(default=0, verbose_name='Cantidad', null=True, blank=True)
    types= models.CharField(max_length=20, choices=operation_choices, verbose_name='Tipo de Operacion', null=True, blank=True)
    operaOut= models.ForeignKey(Output, on_delete=models.SET_NULL, null=True, blank=True,related_name='invOutput_id')
    operaIn= models.ForeignKey(Input, on_delete=models.SET_NULL, null=True, blank=True,related_name='invInput_id')
    operaMove= models.ForeignKey(Movement, on_delete=models.SET_NULL, null=True, blank=True,related_name='invMove_id')
    operaAdjustment= models.ForeignKey(Adjustment, on_delete=models.SET_NULL, null=True, blank=True,related_name='invAdjustment_id')

    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.store

    def toJSON(self):
        item = model_to_dict(self, exclude=['storeinv_in_store','storeinv_out_store'])
        item['types'] = {'id': self.types, 'name': self.get_types_display()}
        item['prod'] = self.prod.toJSON()
        item['in_store'] = self.in_store.toJSON()
        item['out_store'] = self.out_store.toJSON()
        item['created_at'] = self.created_at.strftime('%Y-%m-%d %H:%M') 
        return item

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        ordering = ['id']


class Config(models.Model):
    cambioVentaDolarBs = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    cambioVentaDolarCop = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)
 

    def toJSON(self):
        item = model_to_dict(self, exclude=['created_at','updated_at'])
        item['cambioVentaDolarBs'] = format(self.cambioVentaDolarBs, '.2f')
        item['cambioVentaDolarCop'] = format(self.cambioVentaDolarCop, '.2f')
        return item
        
    @receiver(user_logged_in)
    def crear_primer_registro_config(sender, user, request, **kwargs):#crear el primer registro de manera automatica
        if not Config.objects.exists():
            config = Config()
            config.cambioVentaDolarBs = 1.00
            config.cambioVentaDolarCop = 1.00
            config.save()

    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'
        ordering = ['id']

class Closing(models.Model):
    observation =models.CharField(max_length=200, null=True, blank=True)
    date_joined = models.DateTimeField(default=datetime.now)
    date_in = models.DateTimeField(default=datetime.now)
    date_end = models.DateTimeField(default=datetime.now)
    num_input =models.CharField(max_length=20)#almacena un vector con los ID de todas las salidas que se van a clasificar
    cant_input = models.IntegerField(default=0, verbose_name='Cantidad de facturas', null=True, blank=True)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    dolar = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, null=True, blank=True)
    peso = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, null=True, blank=True)
    bolivar = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, null=True, blank=True)
    is_active= models.CharField(max_length=10, choices=status_choices, default='1', verbose_name='Estatus')
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"{self.observation}, {self.date_joined}, {self.date_in}, {self.date_end}, {self.num_input}, {self.cant_input}, {self.total}, {self.dolar}, {self.peso}, {self.bolivar}, {self.is_active}, {self.created_at}, {self.updated_at}"
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['store'])
        item['total'] = format(self.total, '.2f')
        item['dolar'] = format(self.dolar, '.2f')
        item['peso'] = format(self.peso, '.2f')
        item['bolivar'] = format(self.bolivar, '.2f')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d %H:%M')
        item['date_in'] = self.date_in.strftime('%Y-%m-%d %H:%M') 
        item['date_end'] = self.date_end.strftime('%Y-%m-%d %H:%M') 
        return item
    
    def delete(self, using=None, keep_parents=False):
        num_list = self.num_input.split(',')
        vector = [num for num in num_list]
        for clo in vector:
            output = Output.objects.get(id__in=clo) 
            output.status = 0
            output.save()
        super(Closing, self).delete()
    
    class Meta:
        verbose_name = 'Cierre de salidas'
        verbose_name_plural = 'Cierre de salidas'
        ordering = ['id']



