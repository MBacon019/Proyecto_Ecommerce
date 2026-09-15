from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Carrito, Category, ItemCarrito, Orden, Product


class StoreTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cliente1', password='testpass123')
        self.client.login(username='cliente1', password='testpass123')

        self.category = Category.objects.create(name='Cascos', slug='cascos')
        self.producto = Product.objects.create(
            name='Casco Integral',
            slug='casco-integral',
            category=self.category,
            price=Decimal('150.00'),
            stock=10,
            available=True,
        )
        self.carrito = Carrito.objects.create(usuario=self.user)

    def test_crear_producto(self):
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(self.producto.category, self.category)
        self.assertTrue(self.producto.available)

    def test_agregar_al_carrito(self):
        response = self.client.post(
            reverse('agregar_al_carrito', args=[self.producto.id]),
            {'quantity': 3},
        )
        self.assertRedirects(response, reverse('ver_carrito'))
        item = ItemCarrito.objects.get(carrito=self.carrito, product=self.producto)
        self.assertEqual(item.cantidad, 3)

    def test_confirmar_orden_con_stock_suficiente(self):
        ItemCarrito.objects.create(carrito=self.carrito, product=self.producto, cantidad=4)

        response = self.client.post(reverse('confirmar_orden'))

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 6)  # 10 - 4
        self.assertEqual(Orden.objects.filter(usuario=self.user).count(), 1)
        self.assertFalse(ItemCarrito.objects.filter(carrito=self.carrito).exists())

        orden = Orden.objects.get(usuario=self.user)
        self.assertRedirects(response, reverse('orden_confirmada', args=[orden.id]))

    def test_confirmar_orden_sin_stock_suficiente(self):
        ItemCarrito.objects.create(carrito=self.carrito, product=self.producto, cantidad=999)

        response = self.client.post(reverse('confirmar_orden'))

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)  # no debe cambiar
        self.assertEqual(Orden.objects.filter(usuario=self.user).count(), 0)
        self.assertTrue(ItemCarrito.objects.filter(carrito=self.carrito).exists())
        self.assertRedirects(response, reverse('ver_carrito'))
