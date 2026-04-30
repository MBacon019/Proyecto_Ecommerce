from django.contrib import admin
from .models import Product, Category, Carrito, ItemCarrito, Orden, ItemOrden

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'created_at', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario']
    search_fields = ['usuario__username']

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'carrito', 'product', 'cantidad', 'subtotal_display']
    list_filter = ['carrito']
    search_fields = ['product__name', 'carrito__usuario__username']

    def subtotal_display(self, obj):
        return obj.subtotal()
    subtotal_display.short_description = 'Subtotal'

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'fecha', 'total']
    search_fields = ['usuario__username']
    list_filter = ['fecha']

@admin.register(ItemOrden)
class ItemOrdenAdmin(admin.ModelAdmin):
    list_display = ['id', 'orden', 'product', 'cantidad', 'precio', 'subtotal_display']
    search_fields = ['product__name', 'orden__usuario__username']

    def subtotal_display(self, obj):
        return obj.subtotal()
    subtotal_display.short_description = 'Subtotal'
