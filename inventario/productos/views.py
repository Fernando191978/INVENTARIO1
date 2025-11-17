from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, F
from django.utils import timezone
from .models import Producto, MovimientoStock
from .forms import ProductoForm, MovimientoStockForm, AjusteStockForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class ProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Producto
    template_name = 'productos/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 10
    permission_required = 'productos.view_producto'

    def get_queryset(self):
        queryset = super().get_queryset()
        stock_bajo = self.request.GET.get('stockBajo')
        if stock_bajo:
            queryset = queryset.filter(stock__lt=F('stock_minimo'))
        return queryset.order_by('nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock_bajo'] = self.request.GET.get('stockBajo', '')
        return context

class ProductoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Producto
    template_name = 'productos/producto_detail.html'
    context_object_name = 'producto'
    #Restriccion de permisos para grupo stock
    permission_required = 'productos.view_producto'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimientos'] = self.object.movimientos.all()[:10] # type: ignore
        context['form_ajuste'] = AjusteStockForm()
        return context

class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('productos:producto_list')
    #Restriccion de permisos para grupo stock
    permission_required = 'productos.add_producto'
    
    
    def form_valid(self, form):
         # Si el código está vacío, se generará automáticamente en el save() del modelo
        if not form.cleaned_data['sku']:
            form.instance.sku = ''  # Esto activará la generación automática
        response = super().form_valid(form)
        if form.cleaned_data['stock'] > 0:
            MovimientoStock.objects.create(
                producto=self.object, # type: ignore
                tipo='entrada',
                cantidad=form.cleaned_data['stock'],
                motivo='Stock inicial al crear el producto',
                fecha=timezone.now(),
                usuario=self.request.user.username if self.request.user.is_authenticated else 'Sistema'
            )
        messages.success(self.request, 'Producto creado exitosamente.')
        return response
    
class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('productos:producto_list')

    #Restriccion de permisos para grupo stock
    permission_required = 'productos.change_producto'

    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Producto actualizado exitosamente.')
        return response
    
class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Producto
    template_name = 'productos/producto_delete.html'
    success_url = reverse_lazy('productos:producto_list')
    #Restriccion de permisos para grupo stock
    permission_required = 'productos.delete_producto'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Producto eliminado exitosamente.')
        return response

class MovimientoStockCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = MovimientoStock
    form_class = MovimientoStockForm
    template_name = 'productos/movimiento_stock_form.html'

    #Restriccion de permisos para grupo stock
    permission_required = 'productos.add_movimientostock'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['producto'] = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        producto = get_object_or_404(Producto, pk=self.kwargs['pk'])
        movimiento = form.save(commit=False)
        movimiento.producto = producto
        movimiento.usuario = self.request.user.username if self.request.user.is_authenticated else 'Sistema'
        

        if movimiento.tipo == 'entrada':
            producto.stock += movimiento.cantidad
        elif movimiento.tipo == 'salida':
            if producto.stock >= movimiento.cantidad:
                producto.stock -= movimiento.cantidad
            else:
                form.add_error('cantidad', 'No hay suficiente stock para realizar esta salida.')
                return self.form_invalid(form)
        movimiento.producto.save()
        movimiento.save()
        messages.success(self.request, 'Movimiento de stock registrado exitosamente.')
        
        return redirect('productos:producto_detail', pk=producto.pk)
    
class AjusteStockView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = AjusteStockForm
    template_name = "productos/ajustar_stock.html"

    #Restriccion de permisos para grupo stock
    permission_required = 'productos.change_producto'

    def get_form_kwargs(self):
        
        kwargs = super().get_form_kwargs()
        kwargs["producto"] = get_object_or_404(Producto, pk=self.kwargs["pk"])
        return kwargs
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context["producto"] = get_object_or_404(Producto, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        
        producto = get_object_or_404(Producto, pk=self.kwargs["pk"])
        nueva_cantidad = form.cleaned_data["cantidad"]
        motivo = form.cleaned_data["motivo"] or "Ajuste de stock"

        diferencia = nueva_cantidad - producto.stock

        if diferencia != 0:
            tipo = "entrada" if diferencia > 0 else "salida" 
            MovimientoStock.objects.create(
                producto=producto,
                tipo=tipo,
                cantidad=abs(diferencia),
                motivo=motivo,
                fecha=timezone.now(),
                usuario = self.request.user.username if self.request.user.is_authenticated else "Sistema"
            )

            producto.stock = nueva_cantidad
            producto.save()

            messages.success(self.request, f"Stock actualizado exitosamente")
        else:
            messages.info(self.request, f"El stock no ha cambiado")

        return redirect("productos:producto_detail", pk=producto.pk)
    
class StockBajoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    
    model = Producto
    template_name = "productos/stock_bajo_list.html"
    context_object_name = "productos"

    permission_required = 'productos.view_producto'
    
    def get_queryset(self):
        
        # Se ha corregido la sintaxis. Se usa F() para una comparación eficiente
        return Producto.objects.filter(stock__lt=F("stock_minimo")).order_by("stock")


# Create your views here.
