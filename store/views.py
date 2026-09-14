from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test # Importa user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Product, Category, Carrito, ItemCarrito, Orden, ItemOrden, Profile # Asegúrate de que Profile esté importado
from django.contrib import messages
from django.db.models import Sum
from django.conf import settings
from .forms import ProductForm, ProductStockForm # Asegúrate de que estos formularios existen en forms.py
from django.db import transaction
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.admin.views.decorators import staff_member_required # No lo usaremos directamente en esta solución, pero está bien tenerlo si lo usas en otro lado
from django.utils import timezone # Necesario para timezone.now()


# ---------- FORMULARIO PERSONALIZADO (NO CAMBIA) ----------
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    tipo_usuario = forms.ChoiceField(choices=Profile.TIPO_USUARIO_CHOICES, label="Tipo de usuario")
    rol_password = forms.CharField(
        label="Contraseña especial para rol", 
        required=False, 
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "tipo_usuario")

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        rol_password = cleaned_data.get('rol_password')

        # Definir las contraseñas válidas para roles especiales (definidas en .env)
        PASSWORDS_POR_ROL = {
            'bodega': settings.ROL_PASSWORD_BODEGA,
            'admin': settings.ROL_PASSWORD_ADMIN,
        }

        if tipo_usuario in PASSWORDS_POR_ROL:
            if rol_password != PASSWORDS_POR_ROL[tipo_usuario]:
                raise forms.ValidationError(f"Contraseña especial incorrecta para el rol '{tipo_usuario}'.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Asegúrate de que el perfil se crea automáticamente (con un signal)
            # o créalo aquí si no lo tienes en un signal
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)
            user.profile.tipo_usuario = self.cleaned_data["tipo_usuario"]
            # Para que admin y bodega puedan acceder al admin de Django
            if self.cleaned_data["tipo_usuario"] in ['admin', 'bodega']:
                user.is_staff = True
            else:
                user.is_staff = False # Los clientes no son staff
            user.profile.save()
            user.save() # Guarda los cambios de is_staff
        return user


# ---------- INICIO DE SESIÓN (NO CAMBIA) ----------
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'store/login.html', {'form': form})

# ---------- CERRAR SESIÓN (NO CAMBIA) ----------
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('home')

# ---------- REGISTRO (NO CAMBIA) ----------
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Tu cuenta ha sido creada exitosamente!")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'store/signup.html', {'form': form})

# ---------- PERFIL (NO CAMBIA) ----------
@login_required
def profile(request):
    return render(request, 'store/profile.html', {'user': request.user})

# ---------- TIENDA (NO CAMBIA) ----------
def home_views(request):
    featured_products = Product.objects.filter(available=True).order_by('-created_at')[:4]
    featured_categories = Category.objects.all()[:3]
    all_categories = Category.objects.all()

    productos_mas_vendidos = Product.objects.annotate(
        total_vendidos=Sum('itemorden__cantidad')
    ).filter(
        total_vendidos__gt=0
    ).order_by('-total_vendidos')[:4]

    context = {
        'featured_products': featured_products,
        'featured_categories': featured_categories,
        'all_categories': all_categories,
        'productos_mas_vendidos': productos_mas_vendidos,
    }
    return render(request, 'store/home.html', context)

def product_list_view(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    context = {
        'current_category': category,
        'all_categories': categories,
        'products': products,
    }
    return render(request, 'store/product_list.html', context)

@login_required
def product_detail_view(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, available=True)
    all_categories = Category.objects.all()
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    form = None

    if request.user.is_authenticated:
        # Asegúrate de que el perfil está cargado
        if hasattr(request.user, 'profile'):
            if request.user.profile.tipo_usuario == 'admin':
                # Asegúrate que ProductForm y ProductStockForm están definidos en forms.py y son accesibles
                if request.method == 'POST':
                    form = ProductForm(request.POST, request.FILES, instance=product)
                    if form.is_valid():
                        form.save()
                        messages.success(request, "Producto actualizado correctamente.")
                        return redirect('product_detail', product_slug=product.slug)
                else:
                    form = ProductForm(instance=product)
            elif request.user.profile.tipo_usuario == 'bodega':
                if request.method == 'POST':
                    form = ProductStockForm(request.POST, instance=product)
                    if form.is_valid():
                        form.save()
                        messages.success(request, "Stock actualizado correctamente.")
                        return redirect('product_detail', product_slug=product.slug)
                else:
                    form = ProductStockForm(instance=product)

    context = {
        'product': product,
        'all_categories': all_categories,
        'related_products': related_products,
        'form': form,
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def agregar_al_carrito(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        try:
            cantidad = int(request.POST.get('quantity', 1))
            if cantidad < 1:
                cantidad = 1
        except ValueError:
            cantidad = 1

        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        item_carrito, created = ItemCarrito.objects.get_or_create(carrito=carrito, product=product)

        if not created:
            cantidad_total = item_carrito.cantidad + cantidad
        else:
            cantidad_total = cantidad

        if cantidad_total > product.stock:
            messages.error(request, f"No hay suficiente stock para agregar {cantidad} unidades. Stock disponible: {product.stock - item_carrito.cantidad}")
            return redirect('product_detail', product_slug=product.slug)

        item_carrito.cantidad = cantidad_total
        item_carrito.save()

        messages.success(request, "Producto agregado al carrito exitosamente.")
        return redirect('ver_carrito')

    return redirect('product_list')

@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)
    total = sum(item.subtotal() for item in items)
    return render(request, 'store/carrito.html', {'items': items, 'total': total})

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id)
    product_name = item.product.name # Obtener nombre antes de eliminar
    item.delete()
    messages.success(request, f'"{product_name}" eliminado del carrito.')
    return redirect('ver_carrito')

@login_required
@transaction.atomic # Asegura que la operación sea atómica
def confirmar_orden(request):
    if request.method == 'POST':
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            items = ItemCarrito.objects.filter(carrito=carrito)

            if not items.exists():
                messages.error(request, "Tu carrito está vacío. No se puede confirmar una orden.")
                return redirect('ver_carrito')

            # Verificar y reducir stock
            for item in items:
                product = item.product
                if item.cantidad > product.stock:
                    messages.error(request, f"No hay suficiente stock para {product.name}. Disponible: {product.stock}.")
                    return redirect('ver_carrito')
            
            total = sum(item.product.price * item.cantidad for item in items)
            orden = Orden.objects.create(usuario=request.user, total=total, fecha=timezone.now()) # Agrega la fecha
            
            for item in items:
                ItemOrden.objects.create(
                    orden=orden,
                    product=item.product,
                    cantidad=item.cantidad,
                    precio=item.product.price
                )
                # Reducir stock DESPUÉS de asegurar que la orden se puede crear
                item.product.stock -= item.cantidad
                item.product.save()

            items.delete() # Vaciar carrito
            messages.success(request, "¡Orden confirmada con éxito!")
            return redirect(reverse('orden_confirmada', args=[orden.id]))

        except Carrito.DoesNotExist:
            messages.error(request, "No tienes un carrito activo.")
            return redirect('product_list') # Redirige a la lista de productos
        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar tu orden: {e}")
            return redirect('ver_carrito')
    return redirect('ver_carrito')


@login_required
def orden_confirmada(request, orden_id):
    # Asegúrate de que el usuario solo vea sus propias órdenes
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    items = ItemOrden.objects.filter(orden=orden)

    return render(request, 'store/orden_confirmada.html', {
        'orden': orden,
        'items': items,
    })
    
# --- Función de test para user_passes_test ---
def is_staff_or_admin(user):
    # Verifica si el usuario está autenticado y tiene un perfil
    if not user.is_authenticated or not hasattr(user, 'profile'):
        return False
    # Verifica si el tipo_usuario es 'admin' o 'bodega'
    return user.profile.tipo_usuario in ['admin', 'bodega']

# --- CAMBIOS AQUÍ: Vista de Historial de Órdenes para CLIENTES ---
@login_required
def historial_ordenes(request):
    """
    Muestra el historial de órdenes para el usuario actualmente autenticado (solo sus propias órdenes).
    """
    # Los clientes normales solo ven sus propias órdenes
    ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha') 

    context = {
        'ordenes': ordenes,
        'es_admin_o_staff': is_staff_or_admin(request.user) # Pasa esta bandera para la plantilla
    }
    return render(request, 'store/historial_ordenes.html', context)

# --- CAMBIOS AQUÍ: Nueva vista de Historial de Órdenes para ADMIN/BODEGA ---
@login_required
@user_passes_test(is_staff_or_admin) # Solo usuarios staff o superusuarios pueden acceder aquí
def historial_ordenes_admin(request):
    """
    Muestra TODAS las órdenes del sistema para personal de bodega y administradores.
    """
    # El personal admin/bodega ve todas las órdenes
    ordenes = Orden.objects.all().order_by('-fecha') 

    context = {
        'ordenes': ordenes,
        'es_admin_o_staff': True # Siempre será True para esta vista
    }
    # Reutilizamos la misma plantilla historial_ordenes.html
    return render(request, 'store/historial_ordenes.html', context)


@login_required
def nota_venta(request, orden_id):
    """
    Muestra la nota de venta para una orden específica,
    con lógica de permisos para clientes y personal.
    """
    orden = get_object_or_404(Orden, id=orden_id)

    # Lógica de permisos: solo el propio usuario o el personal (admin/bodega) pueden ver la nota.
    user_is_staff = False
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.tipo_usuario in ['admin', 'bodega']:
            user_is_staff = True

    if not user_is_staff and orden.usuario != request.user:
        messages.error(request, "No tienes permiso para ver esta nota de venta.")
        return redirect('home') # O a una página de acceso denegado más adecuada

    # ¡LA LÍNEA CLAVE A CAMBIAR ES ESTA!
    # Usa 'orden.items.all()' porque definiste related_name='items' en ItemOrden.
    items = orden.items.all() # <--- ¡Este es el cambio que necesitas hacer!

    context = {
        'orden': orden,
        'items': items,
    }
    return render(request, 'store/nota_venta.html', context)

# --- EDITAR STOCK (NO CAMBIA) ---
@login_required
def editar_stock(request):
    user_profile = request.user.profile
    if user_profile.tipo_usuario not in ['admin', 'bodega']:
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('home')
    
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('stock_'):
                try:
                    product_id = int(key.split('_')[1])
                    nuevo_stock = int(value)
                    product = Product.objects.get(id=product_id)
                    product.stock = max(nuevo_stock, 0)
                    product.save()
                except Exception:
                    continue
        messages.success(request, "Stock actualizado correctamente.")
        return redirect('editar_stock')

    categories = Category.objects.prefetch_related('products').all()
    return render(request, 'store/editar_stock.html', {'categories': categories})


# --- LISTA DE NOTAS DE VENTA (ahora muestra solo para admin/bodega y usa el mismo criterio que historial_ordenes_admin) ---
# --- Tu vista lista_notas_venta (ya la tienes, pero la incluyo para contexto) ---
@login_required
@user_passes_test(is_staff_or_admin, login_url='home') # Se redirige a 'home' si no pasa el test
def lista_notas_venta(request):
    """
    Muestra una lista de todas las notas de venta para personal de bodega y administradores.
    """
    ordenes = Orden.objects.all().order_by('-fecha') # Ordenar por fecha, la más reciente primero

    return render(request, 'store/lista_notas_venta.html', {'ordenes': ordenes})

# --- ACTUALIZAR CANTIDAD CARRITO (NO CAMBIA) ---
def actualizar_cantidad_carrito(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ItemCarrito, id=item_id)
        
        try:
            nueva_cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return redirect('ver_carrito')

        if nueva_cantidad <= 0:
            product_name = item.product.name
            item.delete()
            messages.success(request, f'"{product_name}" eliminado del carrito.')
        else:
            if nueva_cantidad > item.product.stock:
                messages.error(request, f'No puedes añadir más de {item.product.stock} unidades de "{item.product.name}".')
            else:
                item.cantidad = nueva_cantidad
                item.save()
                messages.success(request, f'Cantidad de "{item.product.name}" actualizada a {nueva_cantidad}.')
    
    return redirect('ver_carrito')

@login_required
def checkout(request):
    """
    Muestra el resumen del carrito del usuario antes de la confirmación final de la orden.
    Permite al usuario revisar los ítems.
    """
    try:
        carrito = Carrito.objects.get(usuario=request.user)
    except Carrito.DoesNotExist:
        # Si el carrito no existe (es poco probable con login_required pero bueno tenerlo)
        messages.info(request, "Tu carrito está vacío.")
        return redirect('product_list') # O a la vista de inicio de productos

    items = ItemCarrito.objects.filter(carrito=carrito)
    total = sum(item.subtotal() for item in items)

    if not items.exists():
        messages.warning(request, "Tu carrito está vacío. Añade productos antes de proceder.")
        return redirect('ver_carrito') # Redirige al carrito vacío

    context = {
        'items': items,
        'total': total,
        # Aquí puedes añadir más datos si necesitas, como un formulario de dirección,
        # opciones de envío, o un campo para una nota (que luego pasarías a confirmar_orden).
    }
    return render(request, 'store/checkout.html', context)