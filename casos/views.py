from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.db.models import ProtectedError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Cliente, Caso, EstadoCaso, Expediente, Pago
from .forms import ClienteForm


def lista_clientes(request):
    clientes = Cliente.objects.all().order_by('nombres')
    return render(request, 'casos/clientes_lista.html', {'clientes': clientes})


def crear_cliente(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_clientes')
    return render(request, 'casos/cliente_form.html', {'form': form, 'titulo': 'Nuevo cliente'})


def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        return redirect('lista_clientes')
    return render(request, 'casos/cliente_form.html', {'form': form, 'titulo': 'Editar cliente'})


def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    error = None
    if request.method == 'POST':
        try:
            cliente.delete()
            return redirect('lista_clientes')
        except ProtectedError:
            error = 'No se puede eliminar: el cliente tiene casos registrados.'
    return render(request, 'casos/cliente_confirmar_eliminar.html', {'cliente': cliente, 'error': error})


def lista_casos(request):
    if 'estado' in request.GET:
        estado_id = request.GET['estado']
    else:
        estado_id = request.COOKIES.get('ultimo_estado', '')

    casos = Caso.objects.select_related('cliente', 'estado').prefetch_related('abogados')
    if estado_id.isdigit():
        casos = casos.filter(estado_id=estado_id)

    response = render(request, 'casos/casos_lista.html', {
        'casos': casos,
        'estados': EstadoCaso.objects.all(),
        'estado_sel': estado_id,
    })
    if 'estado' in request.GET:
        response.set_cookie('ultimo_estado', estado_id, max_age=60 * 60 * 24 * 7)
    return response


def detalle_caso(request, pk):
    caso = get_object_or_404(Caso, pk=pk)
    return render(request, 'casos/caso_detalle.html', {
        'caso': caso,
        'expedientes': caso.expedientes.all(),
        'pagos': caso.pagos.all(),
    })


def registrar_pago(request, pk):
    caso = get_object_or_404(Caso, pk=pk)
    if request.method == 'POST':
        try:
            monto = Decimal(request.POST.get('monto', ''))
        except InvalidOperation:
            monto = None
        descripcion = request.POST.get('descripcion') or 'Pago registrado'

        if monto is None or monto <= 0:
            messages.error(request, 'Monto inválido.')
        elif not caso.estado.permite_pagos:
            messages.error(request, f'Pago rechazado: el caso está "{caso.estado.nombre}" y no admite pagos.')
        else:
            Pago.objects.create(caso=caso, monto=monto, fecha=timezone.localdate(), descripcion=descripcion)
            messages.success(request, f'Pago de S/ {monto} registrado correctamente.')
    return redirect('detalle_caso', pk=pk)


def subir_documento(request, pk):
    expediente = get_object_or_404(Expediente, pk=pk)
    if request.method == 'POST' and request.FILES.get('documento'):
        expediente.documento = request.FILES['documento']
        expediente.save()
        messages.success(request, f'Documento subido al expediente {expediente.numero}.')
    else:
        messages.error(request, 'Selecciona un archivo.')
    return redirect('detalle_caso', pk=expediente.caso.pk)


def api_caso(request, pk):
    caso = get_object_or_404(Caso, pk=pk)
    return JsonResponse({
        'codigo': caso.codigo,
        'cliente': caso.cliente.nombres,
        'estado': caso.estado.nombre,
        'abogados': [a.username for a in caso.abogados.all()],
        'expedientes': caso.expedientes.count(),
        'total_pagado': float(caso.total_pagado()),
    })