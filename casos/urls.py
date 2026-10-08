from django.urls import path
from . import views

urlpatterns = [
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.crear_cliente, name='crear_cliente'),
    path('clientes/<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    path('clientes/<int:pk>/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),
    path('casos/', views.lista_casos, name='lista_casos'),
    path('casos/<int:pk>/', views.detalle_caso, name='detalle_caso'),
    path('casos/<int:pk>/pago/', views.registrar_pago, name='registrar_pago'),
    path('expedientes/<int:pk>/documento/', views.subir_documento, name='subir_documento'),
    path('casos/api/<int:pk>/', views.api_caso, name='api_caso'),
]