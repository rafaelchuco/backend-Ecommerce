from django.test import TestCase
from django.contrib.auth.models import User
from .models import Cart, CartItem
from applications.products.models import Product

class CartTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(name='Silla', price=50, stock=20, is_active=True)
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_total_price(self):
        self.assertEqual(self.cart.total_price, 100)

    def test_total_items(self):
        self.assertEqual(self.cart.total_items, 2)

    def test_add_item(self):
        new_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(self.cart.total_items, 5)

    def test_remove_item(self):
        self.cart_item.delete()
        self.assertEqual(self.cart.items.count(), 0)
