from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.VentaListView.as_view(), name='venta_list'),
    path('nueva/', views.VentaCreateView.as_view(), name='venta_create'),
    path('<int:pk>/', views.VentaDetailView.as_view(), name='venta_detail'),
    path('<int:pk>/editar/', views.VentaUpdateView.as_view(), name='venta_update'),
    path('<int:pk>/eliminar/', views.VentaDeleteView.as_view(), name='venta_delete'),
    path('producto/<int:producto_id>/precio/', views.ProductoPrecioView.as_view(), name='producto_precio'),
    path('<int:pk>/pdf/', views.venta_pdf, name='venta_pdf'),
    path('grafico/ventas-dia/', views.ventas_por_dia, name='ventas_por_dia'),
]