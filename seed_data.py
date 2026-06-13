import os
import sys
import subprocess

# Reconfigure stdout/stderr to support Vietnamese characters on Windows console
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

workspace = os.environ.get("WORKSPACE", os.path.dirname(os.path.abspath(__file__)))
python_exe = os.environ.get("PYTHON_EXE", sys.executable)

def run_seed_subprocess(service_name):
    print(f"Starting subprocess for {service_name}...")
    subprocess.run([python_exe, "seed_data.py", "--service", service_name], check=True)

def seed_user_service():
    print("Seeding User Service...")
    sys.path.insert(0, os.path.join(workspace, "services", "user-service"))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    
    from user_app.models import User, Address
    
    # Clean old data
    Address.objects.all().delete()
    User.objects.all().delete()
    
    # Create customers
    c1 = User.objects.create_user(
        username="customer1",
        password="password123",
        email="customer1@example.com",
        role="customer",
        full_name="Nguyen Van A",
        phone="0912345678"
    )
    admin1 = User.objects.create_superuser(username="admin1", password="password123", email="admin1@example.com")
    admin1.role = "admin"
    admin1.full_name = "Admin Demo"
    admin1.phone = "0900000001"
    admin1.save()
    User.objects.create_user(
        username="staff1",
        password="password123",
        email="staff1@example.com",
        role="staff",
        full_name="Tran Thi Staff",
        phone="0900000002"
    )
    User.objects.create_user(
        username="shipper1",
        password="password123",
        email="shipper1@example.com",
        role="shipper",
        full_name="Le Van Shipper",
        phone="0900000003"
    )
    
    # Create address
    Address.objects.create(
        user=c1,
        full_name="Nguyen Van A",
        phone="0912345678",
        address_line="144 Xuan Thuy, Cau Giay, Ha Noi",
        is_default=True
    )
    print("User Service seeded. (Customer ID:", c1.id, ")")

def seed_product_service():
    print("Seeding Product Service...")
    sys.path.insert(0, os.path.join(workspace, "services", "product-service"))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    
    from product_app.models import Category, Product, Book, Electronic, Fashion
    
    # Clean old data
    Book.objects.all().delete()
    Electronic.objects.all().delete()
    Fashion.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    
    # Create categories
    cat_book = Category.objects.create(name="Sách", description="Sách khoa học, lập trình, văn học")
    cat_elec = Category.objects.create(name="Điện tử", description="Điện thoại, Laptop, linh kiện")
    cat_fashion = Category.objects.create(name="Thời trang", description="Quần áo, giày dép, phụ kiện")
    
    # Create Book
    b = Book.objects.create(
        name="Lập trình Django Python từ cơ bản đến nâng cao",
        price=150000.00,
        stock=50,
        description="Cuốn sách hướng dẫn chi tiết phát triển Web với Django.",
        category=cat_book,
        author="Guido van Rossum",
        publisher="NXB Bach Khoa",
        isbn="978-604-1-1234-5",
        page=350,
        language="Tiếng Việt"
    )
    
    # Create Electronic
    e = Electronic.objects.create(
        name="Laptop Dell XPS 15",
        price=35000000.00,
        stock=10,
        description="Laptop doanh nhân cao cấp màn hình OLED cực đẹp.",
        category=cat_elec,
        brand="Dell",
        warranty="12 tháng",
        model="XPS 9520",
        power="130W"
    )
    
    # Create Fashion
    f = Fashion.objects.create(
        name="Áo khoác gió thể thao",
        price=450000.00,
        stock=100,
        description="Áo khoác chống nước nhẹ, thoáng khí.",
        category=cat_fashion,
        size="L",
        color="Xanh Navy",
        material="Polyester",
        gender="Nam"
    )
    print("Product Service seeded. Products created:")
    print(f"- Book (ID: {b.id}): {b.name}")
    print(f"- Electronic (ID: {e.id}): {e.name}")
    print(f"- Fashion (ID: {f.id}): {f.name}")

def seed_gateway_service():
    print("Seeding Gateway Service...")
    sys.path.insert(0, os.path.join(workspace, "services", "gateway-service"))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    
    from gateway_app.models import Customer
    
    Customer.objects.all().delete()
    Customer.objects.create(
        full_name="Nguyen Van A",
        email="customer1@example.com",
        phone="0912345678",
        address="144 Xuan Thuy, Cau Giay, Ha Noi"
    )
    print("Gateway Service seeded.")

def clear_cart_service():
    print("Clearing Cart Service...")
    sys.path.insert(0, os.path.join(workspace, "services", "cart-service"))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from cart_app.models import CartItem, Cart
    CartItem.objects.all().delete()
    Cart.objects.all().delete()
    print("Cart Service cleared.")

def clear_order_service():
    print("Clearing Order Service...")
    sys.path.insert(0, os.path.join(workspace, "services", "order-service"))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from order_app.models import OrderItem, Order
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    print("Order Service cleared.")

def clear_payment_service():
    print("Clearing Payment Service...")
    sys.path.insert(0, os.path.join(workspace, "services", "payment-service"))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from payment_app.models import Payment
    Payment.objects.all().delete()
    print("Payment Service cleared.")

def clear_shipping_service():
    print("Clearing Shipping Service...")
    sys.path.insert(0, os.path.join(workspace, "services", "shipping-service"))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from shipping_app.models import Shipment
    Shipment.objects.all().delete()
    print("Shipping Service cleared.")

def clear_ai_service():
    print("Clearing AI Service...")
    sys.path.insert(0, os.path.join(workspace, "services", "ai-service"))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from ai_app.models import UserBehavior
    UserBehavior.objects.all().delete()
    print("AI Service cleared.")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--service":
        svc = sys.argv[2]
        if svc == "user":
            seed_user_service()
        elif svc == "product":
            seed_product_service()
        elif svc == "gateway":
            seed_gateway_service()
        elif svc == "cart":
            clear_cart_service()
        elif svc == "order":
            clear_order_service()
        elif svc == "payment":
            clear_payment_service()
        elif svc == "shipping":
            clear_shipping_service()
        elif svc == "ai":
            clear_ai_service()
    else:
        run_seed_subprocess("ai")
        run_seed_subprocess("shipping")
        run_seed_subprocess("payment")
        run_seed_subprocess("order")
        run_seed_subprocess("cart")
        run_seed_subprocess("user")
        run_seed_subprocess("product")
        run_seed_subprocess("gateway")
        print("All seeding completed successfully!")
