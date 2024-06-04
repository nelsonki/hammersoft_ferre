
from django.urls import path
from core.reports.views.input.views import *
from core.reports.views.output.views import *
from core.reports.views.inventary.views import *
urlpatterns = [
    #reportes de salida
    path('output/', ReportOutputView.as_view(), name='output_report'),
    path('input/', ReportInputView.as_view(), name='input_report'),
    path('inventary/', ReportInventaryView.as_view(), name='inventary_report'),
    path('inventaryProd/', ReportProductOutputView.as_view(), name='inventaryprod_report'),
    path('inventaryProdStore/', ReportProductStoreView.as_view(), name='inventaryprodstore_report'),
    path('inventaryProdPvp/', ReportProductPvpView.as_view(), name='inventaryprodpvp_report'),
    path('inventaryProdFisico/', ReportProductFisicoView.as_view(), name='inventaryprodfisico_report'),

]