import io
import random
import string
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.utils import timezone

from PIL import Image

from applications.products.models import (
    Category,
    Brand,
    Material,
    Product,
    ProductImage,
    ProductSpecification,
    Review,
)
from applications.orders.models import Order, OrderItem, OrderStatusHistory, Coupon
from applications.cart.models import Cart, CartItem, Wishlist
from applications.users.models import UserProfile, Address


class Command(BaseCommand):
    help = "Seed fake data for all models except users."

    def add_arguments(self, parser):
        parser.add_argument("--seed", type=int, default=None, help="Random seed")
        parser.add_argument("--products", type=int, default=100)
        parser.add_argument("--categories", type=int, default=8)
        parser.add_argument("--brands", type=int, default=8)
        parser.add_argument("--materials", type=int, default=8)
        parser.add_argument("--max-images", type=int, default=3)
        parser.add_argument("--max-specs", type=int, default=4)
        parser.add_argument("--reviews", type=int, default=200)
        parser.add_argument("--orders", type=int, default=30)
        parser.add_argument("--max-order-items", type=int, default=5)
        parser.add_argument("--carts", type=int, default=15)
        parser.add_argument("--max-cart-items", type=int, default=6)
        parser.add_argument("--wishlists", type=int, default=50)
        parser.add_argument("--coupons", type=int, default=10)
        parser.add_argument("--addresses-per-user", type=int, default=2)

    def handle(self, *args, **options):
        if options["seed"] is not None:
            random.seed(options["seed"])

        self.stdout.write("Seeding fake data (no users will be created)...")

        users = list(User.objects.all())
        has_users = len(users) > 0

        categories = self._ensure_categories(options["categories"])
        brands = self._ensure_brands(options["brands"])
        materials = self._ensure_materials(options["materials"])
        products = self._create_products(
            options["products"], categories, brands, materials
        )

        self._create_specs(products, options["max_specs"])
        self._create_images(products, options["max_images"])
        self._create_coupons(options["coupons"])

        carts = self._create_carts(
            products, users, options["carts"], options["max_cart_items"]
        )
        self._create_wishlists(products, users, options["wishlists"])

        if has_users:
            self._ensure_profiles_and_addresses(users, options["addresses_per_user"])
            self._create_reviews(products, users, options["reviews"])
            self._create_orders(
                products, users, options["orders"], options["max_order_items"]
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "No users found. Skipping reviews, orders, wishlists for users, "
                    "profiles, and addresses."
                )
            )

        self.stdout.write(self.style.SUCCESS("Done."))
        self._print_summary()

    def _ensure_categories(self, count):
        base_names = [
            "Living Room",
            "Dining Room",
            "Bedroom",
            "Office",
            "Outdoor",
            "Decor",
            "Lighting",
            "Storage",
            "Kids",
            "Bathroom",
        ]
        categories = []
        for i in range(count):
            name = base_names[i % len(base_names)]
            if i >= len(base_names):
                name = f"{name} {i + 1}"
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"Category for {name} products.",
                    "is_active": True,
                    "order": i,
                },
            )
            categories.append(category)
        return categories

    def _ensure_brands(self, count):
        base_names = [
            "Nordic Home",
            "Urban Line",
            "Crafted Studio",
            "Modern Loft",
            "Classic Oak",
            "Prime Living",
            "Velvet House",
            "Bright Works",
            "Studio Form",
            "Heritage Co",
        ]
        brands = []
        for i in range(count):
            name = base_names[i % len(base_names)]
            if i >= len(base_names):
                name = f"{name} {i + 1}"
            brand, _ = Brand.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"Brand {name}.",
                    "is_active": True,
                },
            )
            brands.append(brand)
        return brands

    def _ensure_materials(self, count):
        base_names = [
            "Wood",
            "Metal",
            "Glass",
            "Leather",
            "Fabric",
            "Marble",
            "Bamboo",
            "Rattan",
            "Concrete",
            "Plastic",
        ]
        materials = []
        for i in range(count):
            name = base_names[i % len(base_names)]
            if i >= len(base_names):
                name = f"{name} {i + 1}"
            material, _ = Material.objects.get_or_create(
                name=name, defaults={"description": f"Material {name}."}
            )
            materials.append(material)
        return materials

    def _create_products(self, count, categories, brands, materials):
        product_names = [
            "Sofa",
            "Chair",
            "Coffee Table",
            "Desk",
            "Bookshelf",
            "Side Table",
            "Wardrobe",
            "Bed Frame",
            "Floor Lamp",
            "Wall Mirror",
            "Bench",
            "Console",
            "Cabinet",
            "Stool",
            "TV Stand",
            "Nightstand",
            "Dining Table",
            "Accent Chair",
            "Shelf",
            "Armchair",
        ]
        colors = ["Black", "White", "Gray", "Beige", "Brown", "Blue", "Green"]
        products = []
        sku_cache = set(Product.objects.values_list("sku", flat=True))

        for i in range(count):
            name = random.choice(product_names)
            sku = self._unique_sku(sku_cache)
            price = self._money(random.uniform(80, 5000))
            discount_price = None
            if random.random() < 0.35:
                discount_pct = random.choice([10, 15, 20, 25, 30])
                discount_price = self._money(
                    price * Decimal(1 - (discount_pct / 100))
                )
            product = Product.objects.create(
                name=f"{name} {i + 1}-{sku}",
                sku=sku,
                description=f"Premium {name.lower()} with durable materials and clean design.",
                category=random.choice(categories),
                brand=random.choice(brands),
                price=price,
                discount_price=discount_price,
                stock=random.randint(0, 120),
                min_stock=5,
                width=self._money(random.uniform(40, 260)),
                height=self._money(random.uniform(40, 220)),
                depth=self._money(random.uniform(30, 180)),
                weight=self._money(random.uniform(2, 90)),
                color=random.choice(colors),
                warranty_months=random.choice([12, 24, 36]),
                assembly_required=random.choice([True, False]),
                assembly_time_minutes=random.randint(15, 240)
                if random.random() < 0.5
                else None,
                is_featured=random.random() < 0.2,
                is_active=True,
                is_new=random.random() < 0.35,
                views_count=random.randint(0, 1000),
            )
            product.materials.set(
                random.sample(materials, k=random.randint(1, min(3, len(materials))))
            )
            products.append(product)

        return products

    def _create_specs(self, products, max_specs):
        spec_names = [
            "Finish",
            "Style",
            "Assembly",
            "Care",
            "Warranty",
            "Origin",
            "Package",
            "Frame",
            "Upholstery",
        ]
        spec_values = [
            "Matte",
            "Gloss",
            "Modern",
            "Classic",
            "Minimal",
            "Indoor",
            "Outdoor",
            "Easy",
            "Premium",
            "Standard",
        ]
        for product in products:
            count = random.randint(1, max_specs)
            for order in range(count):
                ProductSpecification.objects.create(
                    product=product,
                    name=random.choice(spec_names),
                    value=random.choice(spec_values),
                    order=order,
                )

    def _create_images(self, products, max_images):
        for product in products:
            count = random.randint(1, max_images)
            for order in range(count):
                image_bytes = self._make_image_bytes()
                image_name = f"product_{product.id}_{order + 1}.png"
                image_file = ContentFile(image_bytes)
                image = ProductImage(
                    product=product,
                    is_primary=(order == 0),
                    alt_text=f"{product.name} image {order + 1}",
                    order=order,
                )
                image.image.save(image_name, image_file, save=False)
                image.save()

    def _create_reviews(self, products, users, count):
        if not users or not products:
            return
        max_pairs = len(users) * len(products)
        target = min(count, max_pairs)
        used_pairs = set()
        created = 0

        while created < target:
            user = random.choice(users)
            product = random.choice(products)
            key = (user.id, product.id)
            if key in used_pairs:
                continue
            used_pairs.add(key)
            Review.objects.create(
                product=product,
                user=user,
                rating=random.randint(1, 5),
                title=random.choice(
                    [
                        "Great value",
                        "Solid build",
                        "Looks amazing",
                        "Comfortable",
                        "Nice finish",
                    ]
                ),
                comment="Good quality and delivered as expected.",
                is_verified_purchase=random.random() < 0.5,
                is_approved=True,
            )
            created += 1

    def _create_coupons(self, count):
        for _ in range(count):
            code = self._unique_code("SAVE", 6)
            discount_type = random.choice(["percent", "amount"])
            discount_value = (
                self._money(random.uniform(5, 30))
                if discount_type == "amount"
                else self._money(random.uniform(5, 30))
            )
            Coupon.objects.get_or_create(
                code=code,
                defaults={
                    "discount_type": discount_type,
                    "discount_value": discount_value,
                    "is_active": True,
                    "expires_at": timezone.now() + timedelta(days=random.randint(10, 90)),
                    "usage_limit": random.choice([None, 50, 100, 200]),
                    "used_count": 0,
                },
            )

    def _create_orders(self, products, users, count, max_items):
        if not products or not users:
            return
        products_in_stock = [p for p in products if p.stock > 0]
        if not products_in_stock:
            return

        for _ in range(count):
            user = random.choice(users)
            item_count = random.randint(1, max_items)
            items = random.sample(
                products_in_stock, k=min(item_count, len(products_in_stock))
            )

            subtotal = Decimal("0.00")
            order = Order.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}".strip() or user.username,
                email=user.email or f"{user.username}@example.com",
                phone="+10000000000",
                address_line1="123 Main St",
                address_line2="",
                city="Metro City",
                state="State",
                postal_code="00000",
                country="Chile",
                subtotal=Decimal("0.00"),
                shipping_cost=self._money(random.uniform(5, 25)),
                tax=Decimal("0.00"),
                discount=Decimal("0.00"),
                total=Decimal("0.00"),
                status=random.choice(["pending", "confirmed", "processing", "shipped"]),
                payment_method=random.choice(
                    ["credit_card", "debit_card", "transfer", "cash"]
                ),
                is_paid=random.random() < 0.8,
                paid_at=timezone.now() if random.random() < 0.8 else None,
                order_notes="Handle with care.",
                tracking_number=self._tracking_number(),
                estimated_delivery=timezone.now().date()
                + timedelta(days=random.randint(3, 14)),
            )

            for product in items:
                qty = random.randint(1, min(3, max(product.stock, 1)))
                line_total = product.final_price * qty
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.sku,
                    product_price=product.final_price,
                    quantity=qty,
                    subtotal=line_total,
                )
                subtotal += line_total

                product.stock = max(product.stock - qty, 0)
                product.save(update_fields=["stock"])

            order.tax = self._money(subtotal * Decimal("0.18"))
            if random.random() < 0.3:
                order.discount = self._money(random.uniform(5, 40))
            order.subtotal = self._money(subtotal)
            order.total = self._money(
                order.subtotal + order.shipping_cost + order.tax - order.discount
            )
            order.save(update_fields=["subtotal", "tax", "discount", "total"])

            if random.random() < 0.6:
                OrderStatusHistory.objects.create(
                    order=order,
                    status="processing",
                    comment="Order processing",
                    created_by=user,
                )

    def _create_carts(self, products, users, count, max_items):
        carts = []
        if not products:
            return carts

        for i in range(count):
            if users and random.random() < 0.7:
                user = random.choice(users)
                cart = Cart.objects.create(user=user, is_active=True)
            else:
                cart = Cart.objects.create(
                    user=None,
                    session_id=self._session_id(),
                    is_active=True,
                )
            carts.append(cart)

            product_choices = random.sample(
                products, k=min(random.randint(1, max_items), len(products))
            )
            for product in product_choices:
                CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={"quantity": random.randint(1, 4)},
                )

        return carts

    def _create_wishlists(self, products, users, count):
        if not users or not products:
            return
        created = 0
        used_pairs = set()
        max_pairs = len(users) * len(products)
        target = min(count, max_pairs)
        while created < target:
            user = random.choice(users)
            product = random.choice(products)
            key = (user.id, product.id)
            if key in used_pairs:
                continue
            used_pairs.add(key)
            Wishlist.objects.create(
                user=user,
                product=product,
                notes="Nice item for later.",
            )
            created += 1

    def _ensure_profiles_and_addresses(self, users, addresses_per_user):
        for user in users:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if not profile.phone:
                profile.phone = "+10000000000"
            if not profile.default_city:
                profile.default_city = "Metro City"
            if not profile.default_state:
                profile.default_state = "State"
            if not profile.default_address_line1:
                profile.default_address_line1 = "123 Main St"
            profile.save()

            existing = Address.objects.filter(user=user).count()
            to_create = max(addresses_per_user - existing, 0)
            for i in range(to_create):
                Address.objects.create(
                    user=user,
                    label=f"Address {i + 1}",
                    address_line1=f"{100 + i} Main St",
                    address_line2="",
                    city="Metro City",
                    state="State",
                    postal_code="00000",
                    country="Chile",
                    is_default=(existing == 0 and i == 0),
                )

    def _make_image_bytes(self):
        color = (
            random.randint(40, 210),
            random.randint(40, 210),
            random.randint(40, 210),
        )
        image = Image.new("RGB", (640, 480), color)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def _unique_sku(self, sku_cache):
        while True:
            sku = f"SKU-{random.randint(100000, 999999)}"
            if sku not in sku_cache:
                sku_cache.add(sku)
                return sku

    def _unique_code(self, prefix, length):
        while True:
            suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
            code = f"{prefix}{suffix}"
            if not Coupon.objects.filter(code=code).exists():
                return code

    def _tracking_number(self):
        return "TRK" + "".join(random.choices(string.digits, k=10))

    def _session_id(self):
        return "sess_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=24))

    def _money(self, value):
        return Decimal(value).quantize(Decimal("0.01"))

    def _print_summary(self):
        self.stdout.write(
            f"Categories: {Category.objects.count()} | "
            f"Brands: {Brand.objects.count()} | "
            f"Materials: {Material.objects.count()} | "
            f"Products: {Product.objects.count()}"
        )
        self.stdout.write(
            f"Images: {ProductImage.objects.count()} | "
            f"Specs: {ProductSpecification.objects.count()} | "
            f"Reviews: {Review.objects.count()}"
        )
        self.stdout.write(
            f"Carts: {Cart.objects.count()} | "
            f"Cart items: {CartItem.objects.count()} | "
            f"Wishlists: {Wishlist.objects.count()}"
        )
        self.stdout.write(
            f"Orders: {Order.objects.count()} | "
            f"Order items: {OrderItem.objects.count()} | "
            f"Order history: {OrderStatusHistory.objects.count()} | "
            f"Coupons: {Coupon.objects.count()}"
        )
        self.stdout.write(
            f"Profiles: {UserProfile.objects.count()} | "
            f"Addresses: {Address.objects.count()}"
        )
