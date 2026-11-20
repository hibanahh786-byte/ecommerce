from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from accounts.models import User
from categories.models import Category
from products.models import Product
from orders.models import Order, OrderItem
from PIL import Image, ImageDraw, ImageFont
import io

class Command(BaseCommand):
    help = "Seeds database with initial categories, products, admin and demo user"

    def create_placeholder_image(self, title, color_bg=(67, 97, 238), color_text=(255, 255, 255)):
        img = Image.new('RGB', (600, 400), color=color_bg)
        draw = ImageDraw.Draw(img)
        # Draw some subtle pattern
        draw.rectangle([10, 10, 590, 390], outline=(255, 255, 255), width=2)
        # Draw text
        draw.text((30, 180), title, fill=color_text)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        return ContentFile(buf.getvalue(), name=f"{title.lower().replace(' ', '_')}.jpg")

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # 1. Create or get Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ecommerce.com',
                'full_name': 'System Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('AdminPassword123')
        admin_user.role = User.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f"Admin user ready: admin / AdminPassword123"))

        # 2. Create or get regular User
        user, created = User.objects.get_or_create(
            username='john_doe',
            defaults={
                'email': 'john@example.com',
                'full_name': 'John Doe',
                'role': User.Role.USER
            }
        )
        user.set_password('UserPassword123')
        user.role = User.Role.USER
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Customer user ready: john_doe / UserPassword123"))

        # 3. Create Categories
        categories_data = [
            "Electronics",
            "Fashion & Apparel",
            "Home & Living",
            "Books & Stationery"
        ]
        cat_objs = {}
        for cname in categories_data:
            cat, _ = Category.objects.get_or_create(name=cname)
            cat_objs[cname] = cat
        self.stdout.write(self.style.SUCCESS(f"Categories seeded: {len(cat_objs)}"))

        # 4. Create Products
        products_data = [
            {
                'name': 'Wireless Noise-Cancelling Headphones',
                'price': 4999.00,
                'stock': 25,
                'category': cat_objs['Electronics'],
                'color': (43, 89, 195)
            },
            {
                'name': 'Smart Fitness Watch Pro',
                'price': 2999.00,
                'stock': 18,
                'category': cat_objs['Electronics'],
                'color': (31, 142, 122)
            },
            {
                'name': 'Ultra-Slim 4K USB-C Monitor',
                'price': 18499.00,
                'stock': 8,
                'category': cat_objs['Electronics'],
                'color': (26, 38, 57)
            },
            {
                'name': 'Classic Cotton Crewneck T-Shirt',
                'price': 799.00,
                'stock': 50,
                'category': cat_objs['Fashion & Apparel'],
                'color': (190, 75, 43)
            },
            {
                'name': 'Ergonomic Executive Office Chair',
                'price': 8999.00,
                'stock': 12,
                'category': cat_objs['Home & Living'],
                'color': (70, 60, 110)
            },
            {
                'name': 'Minimalist Ceramic Desk Lamp',
                'price': 1499.00,
                'stock': 30,
                'category': cat_objs['Home & Living'],
                'color': (140, 100, 50)
            },
            {
                'name': 'Hardcover Dotted Journal Notebook',
                'price': 399.00,
                'stock': 65,
                'category': cat_objs['Books & Stationery'],
                'color': (50, 120, 80)
            },
        ]

        created_products = []
        for pdata in products_data:
            prod, p_created = Product.objects.get_or_create(
                name=pdata['name'],
                defaults={
                    'price': pdata['price'],
                    'stock': pdata['stock'],
                    'category': pdata['category']
                }
            )
            if not prod.image:
                img_file = self.create_placeholder_image(pdata['name'], color_bg=pdata['color'])
                prod.image = img_file
                prod.save()
            created_products.append(prod)

        self.stdout.write(self.style.SUCCESS(f"Products seeded: {len(created_products)}"))

        # 5. Create a sample initial order if none exist
        if Order.objects.count() == 0 and len(created_products) >= 2:
            p1 = created_products[0]
            p2 = created_products[1]
            # Order 1 (Placed)
            o1 = Order.objects.create(
                user=user,
                total_amount=p1.price * 1,
                status='Placed'
            )
            OrderItem.objects.create(
                order=o1,
                product=p1,
                quantity=1,
                price=p1.price
            )

            # Order 2 (Completed)
            o2 = Order.objects.create(
                user=user,
                total_amount=p2.price * 2,
                status='Completed'
            )
            OrderItem.objects.create(
                order=o2,
                product=p2,
                quantity=2,
                price=p2.price
            )
            self.stdout.write(self.style.SUCCESS("Sample orders created for demonstration."))

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
