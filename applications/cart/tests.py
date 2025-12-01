from django.test import TestCase
from django.contrib.auth.models import User
from .models import Cart, CartItem
from applications.products.models import Product

class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='pass')
        self.product = Product.objects.create(name="Mesa", price=100, stock=10, is_active=True)
        self.cart = Cart.objects.create(user=self.user)
    
    def test_add_item_cart(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(item.subtotal, 200)
        self.assertEqual(self.cart.total_items, 2)

    def test_remove_item_cart(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        item.delete()
        self.assertEqual(self.cart.items.count(), 0)
