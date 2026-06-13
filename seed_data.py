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

def _knowledge_base_entries():
    categories = [
        ("Books", "sach", "sach hoc tap, sach lap trinh, sach van hoc"),
        ("Electronics", "dien tu", "laptop, dien thoai, phu kien cong nghe"),
        ("Fashion", "thoi trang", "ao khoac, ao thun, giay, tui, phu kien"),
        ("Cosmetics", "my pham", "serum, kem duong, son, sua rua mat"),
        ("Toys", "do choi", "do choi tre em, lego, board game, giao duc"),
        ("Sports", "the thao", "bong, vot, giay tap, dung cu tap luyen"),
        ("HomeKitchen", "nha bep", "noi, chau, binh giu nhiet, may xay"),
        ("Food", "thuc pham", "do kho, banh, hat, sua, do uong"),
        ("Office", "van phong", "but, giay, ghe, ban, may in"),
        ("HealthCare", "cham soc suc khoe", "vitamin, may do huyet ap, dung cu y te"),
    ]
    entries = []

    for category, tag, examples in categories:
        entries.extend([
            {
                "title": f"{category}: tu van san pham gia tot",
                "content": (
                    f"Khi nguoi dung hoi ve {tag} gia re, uu tien san pham con hang, gia thap den trung binh, "
                    f"danh gia on dinh va mo ta ro cong dung. Cac vi du lien quan: {examples}. "
                    "Neu co nhieu lua chon, sap xep theo muc phu hop voi nhu cau truoc, gia sau."
                ),
                "category": category,
                "intent": "budget",
                "source_type": "guide",
                "tags": f"{tag}, gia re, tiet kiem, budget",
                "priority": 70,
            },
            {
                "title": f"{category}: tu van san pham chat luong cao",
                "content": (
                    f"Khi nguoi dung can {tag} chat luong cao, uu tien thuong hieu uy tin, bao hanh/han su dung ro rang, "
                    "vat lieu tot, mo ta chi tiet va ton kho du. Neu gia cao, giai thich ly do bang loi ich thuc te."
                ),
                "category": category,
                "intent": "premium",
                "source_type": "guide",
                "tags": f"{tag}, cao cap, chat luong, premium",
                "priority": 65,
            },
            {
                "title": f"{category}: goi y qua tang",
                "content": (
                    f"Voi nhu cau mua {tag} lam qua tang, uu tien san pham pho bien, de su dung, it yeu cau ca nhan hoa, "
                    "gia vua phai va co mo ta loi ich ngan gon. Neu nguoi dung chua noi doi tuong nhan qua, hoi them do tuoi, gioi tinh va ngan sach."
                ),
                "category": category,
                "intent": "gift",
                "source_type": "recommendation_rule",
                "tags": f"{tag}, qua tang, gift, tu van",
                "priority": 60,
            },
        ])

    cross_sell_pairs = [
        ("Electronics", "Office", "Laptop, chuot, ban phim, ghe lam viec va do van phong thuong duoc goi y cung nhau cho nhu cau hoc tap/lam viec."),
        ("Books", "Office", "Sach hoc tap nen goi y kem so tay, but, giay note hoac do dung ban hoc."),
        ("Fashion", "Sports", "Ao khoac, giay the thao va phu kien tap luyen co the goi y theo phong cach nang dong."),
        ("Cosmetics", "HealthCare", "My pham cham soc da co the goi y kem san pham cham soc suc khoe neu nguoi dung quan tam den lam dep an toan."),
        ("HomeKitchen", "Food", "Do nha bep co the goi y kem nguyen lieu, do kho, hat hoac san pham tien ich nau an."),
        ("Toys", "Books", "Do choi giao duc co the goi y kem sach thieu nhi, sach ky nang hoac sach hoc tap."),
        ("Sports", "HealthCare", "Dung cu the thao co the goi y kem san pham cham soc suc khoe, vitamin hoac thiet bi theo doi suc khoe."),
        ("Electronics", "HomeKitchen", "Thiet bi dien tu gia dung va do nha bep thong minh co the goi y khi user tim san pham tien ich cho gia dinh."),
    ]
    for source, target, content in cross_sell_pairs:
        entries.append({
            "title": f"Cross-sell: {source} -> {target}",
            "content": content,
            "category": source,
            "intent": "cross_sell",
            "source_type": "recommendation_rule",
            "tags": f"{source}, {target}, mua kem, cross sell, graph",
            "priority": 72,
        })

    situational_intents = [
        ("student", "Hoc sinh/sinh vien", "Uu tien gia tot, do ben, de su dung, phu hop hoc tap va co gia tri lau dai."),
        ("office_worker", "Nhan vien van phong", "Uu tien san pham giup lam viec hieu qua, thiet ke gon, chat luong on dinh va bao hanh ro."),
        ("parent", "Phu huynh mua cho con", "Uu tien an toan, do tuoi phu hop, chat lieu tot, mo ta ro cach su dung va loi ich giao duc."),
        ("gift_for_male", "Qua tang cho nam", "Uu tien do cong nghe, thoi trang co ban, the thao, sach ky nang hoac do dung thuc te."),
        ("gift_for_female", "Qua tang cho nu", "Uu tien my pham, thoi trang, sach, do gia dung tien ich hoac san pham cham soc suc khoe."),
        ("urgent_need", "Can mua gap", "Uu tien san pham con hang, thong tin ro, gia hop ly, khong de xuat hang het ton kho."),
        ("compare_products", "So sanh san pham", "Khi user muon so sanh, tra loi theo tieu chi gia, tinh nang, doi tuong phu hop, uu diem va han che."),
        ("unknown_need", "Nhu cau chua ro", "Neu query mo ho, hoi lai ngan sach, danh muc, doi tuong su dung va muc uu tien cua nguoi dung."),
    ]
    for intent, title, content in situational_intents:
        entries.append({
            "title": f"Intent: {title}",
            "content": content,
            "category": "General",
            "intent": intent,
            "source_type": "guide",
            "tags": f"{intent}, chatbot, tu van, personalization",
            "priority": 68,
        })

    rag_rules = [
        ("RAG context khong du du lieu", "Neu retrieve khong co ket qua phu hop, chatbot phai noi chua tim thay san pham phu hop va hoi them dieu kien, khong duoc tu bia ten san pham/gia."),
        ("RAG uu tien thong tin moi nhat", "Khi co nhieu entry trung nhau, uu tien entry co priority cao va product con hang. Gia va stock nen lay tu Product Service neu can hien thi cho user."),
        ("RAG tra loi ngan gon", "Cau tra loi tu van nen dua 3-5 goi y, moi goi y co ly do ngan gon. Khong dua qua nhieu san pham lam user kho chon."),
        ("RAG loc theo ngan sach", "Neu query co muc gia, apply price range truoc khi generate. Neu khong co gia, hoi them ngan sach hoac dua nhieu muc gia."),
        ("RAG bao ve ngu canh tieng Viet", "Cac tu khoa tieng Viet va tieng Anh co the tuong duong: laptop/may tinh xach tay, skincare/cham soc da, budget/gia re."),
        ("RAG ket hop graph", "Sau semantic search, dung graph/category relationship de loai ket qua lech danh muc va them san pham mua kem hop ly."),
    ]
    for title, content in rag_rules:
        entries.append({
            "title": title,
            "content": content,
            "category": "RAG",
            "intent": "rag_rule",
            "source_type": "recommendation_rule",
            "tags": "rag, retrieve, generate, chatbot, knowledge base",
            "priority": 82,
        })

    entries.extend([
        {
            "title": "Quy tac uu tien san pham con hang",
            "content": "Recommendation khong nen de san pham het hang len dau. Neu san pham phu hop nhung het hang, chi nen goi y nhu lua chon tham khao va dua san pham thay the con hang.",
            "category": "General",
            "intent": "ranking",
            "source_type": "recommendation_rule",
            "tags": "stock, inventory, ranking, recommendation",
            "priority": 100,
        },
        {
            "title": "Quy tac loc dung danh muc",
            "content": "Khi query co danh muc ro rang nhu laptop, sach, my pham, he thong phai loc category truoc khi xep hang. Khong tron san pham khac danh muc neu khong co yeu cau mua kem.",
            "category": "General",
            "intent": "category_filter",
            "source_type": "recommendation_rule",
            "tags": "category, filter, rag, graph",
            "priority": 98,
        },
        {
            "title": "Quy tac can bang gia va nhu cau",
            "content": "Neu nguoi dung noi gia re, uu tien gia. Neu noi tot nhat hoặc cao cap, uu tien chat luong va tinh nang. Neu noi vua tam, can bang gia, thuong hieu va danh gia.",
            "category": "General",
            "intent": "price_quality_tradeoff",
            "source_type": "recommendation_rule",
            "tags": "price, quality, budget, premium",
            "priority": 95,
        },
        {
            "title": "Quy tac goi y mua kem",
            "content": "Khi nguoi dung xem hoac mua san pham chinh, goi y phu kien co lien quan trong cung boi canh: laptop kem chuot/ban phim, sach kem so tay, my pham kem bong tay trang, the thao kem tui dung cu.",
            "category": "General",
            "intent": "cross_sell",
            "source_type": "recommendation_rule",
            "tags": "cross sell, frequently bought together, add to cart",
            "priority": 92,
        },
        {
            "title": "Quy tac cold start user moi",
            "content": "Neu user moi chua co hanh vi, fallback sang san pham pho bien, san pham con hang, san pham theo query hien tai va san pham co category trung voi nhu cau.",
            "category": "General",
            "intent": "cold_start",
            "source_type": "recommendation_rule",
            "tags": "cold start, new user, fallback",
            "priority": 90,
        },
        {
            "title": "Quy tac giai thich recommendation",
            "content": "Chatbot nen giai thich ngan gon ly do goi y: cung danh muc, phu hop ngan sach, con hang, lien quan den san pham vua xem, hoac phu hop voi tu khoa trong query.",
            "category": "General",
            "intent": "explainability",
            "source_type": "recommendation_rule",
            "tags": "explainable ai, chatbot, recommendation reason",
            "priority": 88,
        },
        {
            "title": "Chinh sach thanh toan",
            "content": "He thong ho tro thanh toan mo phong. Don hang co the tao payment, payment co trang thai cho xu ly hoac da thanh toan. Khi payment duoc xac nhan, shipping co the duoc tao/cap nhat.",
            "category": "Policy",
            "intent": "payment",
            "source_type": "policy",
            "tags": "payment, thanh toan, order",
            "priority": 80,
        },
        {
            "title": "Chinh sach giao hang",
            "content": "Shipping Service quan ly van don theo order_id, dia chi, trang thai, thoi diem gui va thoi diem giao. Admin co the gan shipper, shipper cap nhat trang thai va ghi chu giao hang.",
            "category": "Policy",
            "intent": "shipping",
            "source_type": "policy",
            "tags": "shipping, giao hang, shipment, shipper",
            "priority": 80,
        },
        {
            "title": "Chinh sach gio hang",
            "content": "Cart luu cac CartItem theo user_id va product_id. Khi them san pham da co trong gio, nen cap nhat so luong thay vi tao dong trung lap.",
            "category": "Policy",
            "intent": "cart",
            "source_type": "policy",
            "tags": "cart, add to cart, quantity",
            "priority": 78,
        },
        {
            "title": "FAQ: toi muon laptop gia re",
            "content": "Hay tim trong category Electronics, uu tien tu khoa laptop, gia thap, con hang. Goi y 3 lua chon va neu co the them phu kien chuot hoac balo laptop.",
            "category": "Electronics",
            "intent": "chatbot_faq",
            "source_type": "faq",
            "tags": "laptop, dien tu, gia re, chatbot",
            "priority": 85,
        },
        {
            "title": "FAQ: toi can sach hoc lap trinh",
            "content": "Hay tim trong category Books, uu tien sach co tu khoa Python, Django, lap trinh, so trang va ngon ngu phu hop. Giai thich sach phu hop nguoi moi hay nang cao.",
            "category": "Books",
            "intent": "chatbot_faq",
            "source_type": "faq",
            "tags": "sach, lap trinh, python, django",
            "priority": 84,
        },
        {
            "title": "FAQ: toi can my pham cho da nhay cam",
            "content": "Hay tim trong category Cosmetics, uu tien san pham co mo ta loai da phu hop, thanh phan diu nhe, han su dung ro rang. Neu thieu thong tin loai da, hoi lai nguoi dung.",
            "category": "Cosmetics",
            "intent": "chatbot_faq",
            "source_type": "faq",
            "tags": "my pham, da nhay cam, skincare",
            "priority": 84,
        },
        {
            "title": "Product fact: Laptop Dell XPS 15",
            "content": "Laptop Dell XPS 15 phu hop nguoi dung can laptop cao cap, man hinh dep, hieu nang tot cho cong viec va hoc tap. Nen goi y khi query co laptop, doanh nhan, cao cap, man hinh dep.",
            "category": "Electronics",
            "intent": "product_fact",
            "source_type": "product",
            "product_id": 2,
            "tags": "Dell, XPS, laptop, premium",
            "priority": 75,
        },
        {
            "title": "Product fact: Sach Django Python",
            "content": "Sach Django Python phu hop nguoi hoc web backend, Python, Django tu co ban den nang cao. Nen goi y khi user search sach lap trinh hoac hoc Django.",
            "category": "Books",
            "intent": "product_fact",
            "source_type": "product",
            "product_id": 1,
            "tags": "Django, Python, sach lap trinh",
            "priority": 75,
        },
        {
            "title": "Product fact: Ao khoac gio the thao",
            "content": "Ao khoac gio the thao phu hop nhu cau thoi trang nam, di chuyen ngoai troi, chong nuoc nhe va thoang khi. Nen goi y khi query co ao khoac, the thao, di mua.",
            "category": "Fashion",
            "intent": "product_fact",
            "source_type": "product",
            "product_id": 3,
            "tags": "ao khoac, thoi trang, the thao",
            "priority": 75,
        },
    ])

    return entries

def clear_ai_service():
    print("Clearing and seeding AI Service...")
    sys.path.insert(0, os.path.join(workspace, "services", "ai-service"))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from ai_app.models import KnowledgeBaseEntry, UserBehavior
    UserBehavior.objects.all().delete()
    KnowledgeBaseEntry.objects.all().delete()

    KnowledgeBaseEntry.objects.bulk_create([
        KnowledgeBaseEntry(**entry) for entry in _knowledge_base_entries()
    ])

    demo_behaviors = [
        UserBehavior(user_id=1, product_id=1, action_type="view"),
        UserBehavior(user_id=1, product_id=2, action_type="view"),
        UserBehavior(user_id=1, product_id=2, action_type="add_to_cart"),
        UserBehavior(user_id=1, product_id=3, action_type="search"),
    ]
    UserBehavior.objects.bulk_create(demo_behaviors)
    print(f"AI Service seeded. Knowledge entries: {KnowledgeBaseEntry.objects.count()}, behaviors: {UserBehavior.objects.count()}")

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
