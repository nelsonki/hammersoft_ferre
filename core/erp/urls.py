from django.urls import path
from core.erp.views.category.views import *
from core.erp.views.dashboard.views import *
from core.erp.views.storeprod.views import *
from core.erp.views.client.views import *
from core.erp.views.product.views import *
from core.erp.views.output.views import *
from core.erp.views.input.views import *
from core.erp.views.movement.views import *
from core.erp.views.order.views import *
from core.erp.views.config.views import *
from  core.erp.views.prodCombo.views import *
from core.erp.views.closing.views import *
from core.erp.views.adjustment.views import *
urlpatterns = [
    #categorias
    path('category/list/', CategoryListView.as_view(), name='category_list'),
    path('category/add/', CategoryCreateView.as_view(), name='category_create'),
    path('category/edit/<int:pk>/', CategoryUpdateView.as_view(), name='category_edit'),
    path('category/delete/<int:pk>/', CategoryDeleteView.as_view(), name='category_delete'),

    #home, panel, dashboard
    path('dashboard', DashboardView.as_view(), name='dashboard'),

    #almacen
    path('storeprod/list/', StoreprodListView.as_view(), name='storeprod_list'),
    path('storeprod/add/', StoreprodCreateView.as_view(), name='storeprod_create'),
    path('storeprod/edit/<int:pk>/', StoreprodUpdateView.as_view(), name='storeprod_edit'),
    path('storeprod/delete/<int:pk>/', StoreprodDeleteView.as_view(), name='storeprod_delete'),

    #Cliente
    path('client/list/', ClientListView.as_view(), name='client_list'),
    path('client/add/', ClientCreateView.as_view(), name='client_create'),
    path('client/edit/<int:pk>/', ClientUpdateView.as_view(), name='client_edit'),
    path('client/delete/<int:pk>/', ClientDeleteView.as_view(), name='client_delete'),

    #Product
    path('product/list/', ProductListView.as_view(), name='product_list'),
    path('product/add/', ProductCreateView.as_view(), name='product_create'),
    path('product/edit/<int:pk>/', ProductUpdateView.as_view(), name='product_edit'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),

    #Producto - Combo
    path('prodcombo/add/', ProdComboCreateView.as_view(), name='prodcombo_create'),
    path('prodcombo/list/', ProdComboListView.as_view(), name='prodcombo_list'),
    path('prodcombo/update/<int:pk>/', ProdComboUpdateView.as_view(), name='prodcombo_update'),
    path('prodcombo/delete/<int:pk>/', ProdComboDeleteView.as_view(), name='prodcombo_delete'),

    #output
    path('output/add/', OutputCreateView.as_view(), name='output_create'),
    path('output/list/', OutputListView.as_view(), name='output_list'),
    path('output/update/<int:pk>/', OutputUpdateView.as_view(), name='output_update'),
    path('output/delete/<int:pk>/', OutputDeleteView.as_view(), name='output_delete'),
    path('output/invoice/pdf/<int:pk>/', OutputInvoicePdfView.as_view(), name='output_invoice_pdf'),
    path('output/grafic/', OutputGraficView.as_view(), name='output_grafic'),

   #input
    path('input/add/', InputCreateView.as_view(), name='input_create'),
    path('input/list/', InputListView.as_view(), name='input_list'),
    path('input/update/<int:pk>/', InputUpdateView.as_view(), name='input_update'),
    path('input/delete/<int:pk>/', InputDeleteView.as_view(), name='input_delete'),
    path('input/invoice/pdf/<int:pk>/', InputInvoicePdfView.as_view(), name='input_invoice_pdf'),
    path('input/grafic/', InputGraficView.as_view(), name='input_grafic'),

    #movement
    path('movement/add/', MovementCreateView.as_view(), name='movement_create'),
    path('movement/list/', MovementListView.as_view(), name='movement_list'),
    path('movement/update/<int:pk>/', MovementUpdateView.as_view(), name='movement_update'),
    path('movement/delete/<int:pk>/', MovementDeleteView.as_view(), name='movement_delete'),
    path('movement/invoice/pdf/<int:pk>/', MovementInvoicePdfView.as_view(), name='movement_invoice_pdf'),

    #order
    path('order/add/', OrderCreateView.as_view(), name='order_create'),
    path('order/list/', OrderListView.as_view(), name='order_list'),
    path('order/update/<int:pk>/', OrderUpdateView.as_view(), name='order_update'),
    path('order/delete/<int:pk>/', OrderDeleteView.as_view(), name='order_delete'),

    #configuraciones
    path('config/update/<int:pk>/', ConfigUpdateView.as_view(), name='config_edit'),

    #closing
    path('closing/add/', ClosingCreateView.as_view(), name='closing_create'),
    path('closing/list/', ClosingListView.as_view(), name='closing_list'),
    path('closing/update/<int:pk>/', ClosingUpdateView.as_view(), name='closing_update'),
    path('closing/delete/<int:pk>/', ClosingDeleteView.as_view(), name='closing_delete'),
    path('closing/invoice/pdf/<int:pk>/', ClosingInvoicePdfView.as_view(), name='closing_invoice_pdf'),


    #adjustment
    path('adjustment/add/', AdjustmentCreateView.as_view(), name='adjustment_create'),
    path('adjustment/list/', AdjustmentListView.as_view(), name='adjustment_list'),
    path('adjustment/delete/<int:pk>/', AdjustmentDeleteView.as_view(), name='adjustment_delete'),
    path('adjustment/invoice/pdf/<int:pk>/', AdjustmentInvoicePdfView.as_view(), name='adjustment_invoice_pdf'),
]
