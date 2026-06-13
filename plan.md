2.1. Xác định yêu cầu 
2.1.1. Functional Requirements 
Hệ thống cần hỗ trợ các chức năng: 
	Quản lý sản phẩm (đa domain: book, electronics, fashion, cosmetics, toys, sports, home 
kitchen, food, office, health care). Được bổ sung thêm 6 sản phẩm so với tiểu luận 1 
	Quản lý người dùng (admin, staff, customer) 
	Giỏ hàng (cart) 
	Đặt hàng (order) 
	Thanh toán (payment) 
	Giao hàng (shipping) 
	Tìm kiếm và gợi ý sản phẩm 
2.1.2. Non-functional Requirements 
	Scalability: Scale từng service độc lập 
	High Availability: Hệ thống luôn sẵn sàng 
	Security: JWT, authentication 
	Maintainability: Dễ bảo trì 
2.2. Phân rã hệ thống theo DDD 
2.2.1. Bounded Context 
Hệ thống được chia thành 8 microservices tương ứng với các Bounded Context riêng biệt:
*   **User Context (`user-service`)**: Quản lý thông tin tài khoản người dùng, phân quyền và địa chỉ.
    *   *Các Class/Model*: `User`, `Address`.
*   **Product Context (`product-service`)**: Quản lý danh mục và các dòng sản phẩm đa ngành hàng.
    *   *Các Class/Model*: `Category`, `Product` và 10 lớp con kế thừa (`Book`, `Electronic`, `Fashion`, `Cosmetic`, `HealthCare`, `Office`, `Food`, `Sports`, `Toys`, `HomeKitchen`).
*   **Cart Context (`cart-service`)**: Quản lý giỏ hàng tạm thời của khách hàng.
    *   *Các Class/Model*: `Cart`, `CartItem`.
*   **Order Context (`order-service`)**: Xử lý đơn đặt hàng và chụp lại giá sản phẩm tại thời điểm mua (price snapshot).
    *   *Các Class/Model*: `Order`, `OrderItem`.
*   **Payment Context (`payment-service`)**: Quản lý các giao dịch thanh toán và cổng thanh toán mô phỏng.
    *   *Các Class/Model*: `Payment`.
*   **Shipping Context (`shipping-service`)**: Quản lý thông tin vận đơn và hành trình giao hàng.
    *   *Các Class/Model*: `Shipment`.
*   **AI Context (`ai-service`)**: Lưu trữ lịch sử hành vi người dùng, phục vụ gợi ý sản phẩm và truy vấn ngữ nghĩa.
    *   *Các Class/Model*: `UserBehavior` (kết hợp ChromaDB để lưu embeddings và Neo4j làm RAG Graph).
*   **Gateway Context (`gateway-service`)**: API Gateway xử lý định tuyến và quản lý thông tin khách hàng giao tiếp UI.
    *   *Các Class/Model*: `Customer`.

2.2.2. Nguyên tắc 
	Mỗi context có database riêng (sử dụng PostgreSQL cho toàn bộ hệ thống để đồng bộ hóa công nghệ)
	Giao tiếp giữa các service qua REST API
2.3. Thiết kế Product Service (Django) 
2.3.1. Phân loại sản phẩm 
Hệ thống sử dụng mô hình kế thừa (được thiết kế theo dạng quan hệ 1-1 Composition từ bảng 
Product gốc) để quản lý các dòng sản phẩm đặc thù: 
	Book: Tác giả, nhà xuất bản, mã ISBN, số trang, ngôn ngữ. 
	Electronics: Thương hiệu, thời hạn bảo hành, model, công suất. 
	Fashion: Kích cỡ, màu sắc, chất liệu, giới tính. 
	Cosmetic: Thương hiệu, loại da phù hợp, ngày hết hạn, xuất xứ. 
	HealthCare: Thương hiệu, thành phần, ngày hết hạn, cách sử dụng (usage). 
	Office: Thương hiệu, chất liệu, màu sắc, kích thước. 
	Food: Thương hiệu, khối lượng (weight), ngày hết hạn, xuất xứ. 
	Sports: Thương hiệu, kích cỡ, khối lượng, loại môn thể thao. 
	Toys: Thương hiệu, độ tuổi phù hợp (age range), chất liệu, số lượng người chơi. 
	HomeKitchen: Thương hiệu, chất liệu, dung tích (capacity), thời hạn bảo hành. 
2.3.2. Class Diagram 
Trong sơ đồ, hệ thống áp dụng quan hệ Generalization (Kế thừa) – được biểu diễn bằng mũi 
tên có đầu hình tam giác rỗng trỏ về thực thể Product cha. Thiết kế này thể hiện mối quan hệ 
"Là một" (Is-A), khẳng định rằng Book, Electronics, hay Fashion bản chất đều là một Product 
nhưng mang các thuộc tính mở rộng khác nhau. 
	Mô hình hóa chuẩn tắc (Is-A Relationship): Thay vì coi các dòng sản phẩm là một 
thành phần con của giỏ hàng/đơn hàng, việc để chúng kế thừa từ Product giúp hệ thống 
tận dụng được tính đa hình (Polymorphic). Toàn bộ các service khác như Cart hay Order 
chỉ cần tương tác và quản lý thực thể chung là Product, giúp giảm thiểu sự phức tạp và 
mang lại sự nhất quán cho hệ thống. 
	Ánh xạ chính xác vào mã nguồn (Multi-table Inheritance): Kiến trúc này khớp hoàn 
toàn với cơ chế Kế thừa đa bảng trong Django ORM. Ở tầng vật lý (Database), cơ sở 
dữ liệu sẽ được triển khai theo dạng Table-per-Type (TPT). Trong đó, bảng cha products 
lưu các thuộc tính dùng chung (name, price, stock, description), còn các bảng con 
(books, electronics,...) sẽ dùng chung product_id vừa làm Khóa chính (Primary Key) vừa làm Khóa ngoại (Foreign Key) kết nối ngược lên. 
	Đảm bảo tính toàn vẹn và Phụ thuộc vòng đời: Dù biểu diễn dưới dạng kế thừa, ràng buộc dữ liệu ở mức database vẫn cài đặt cơ chế ON DELETE CASCADE. Do đó, nếu một sản phẩm cha bị xóa khỏi hệ thống, các bản ghi thông tin đặc thù ở bảng con tương ứng cũng sẽ tự động bị tiêu hủy, tránh triệt để tình trạng rác dữ liệu (orphan records). 
	Tối ưu hóa không gian lưu trữ (Sparse Table Avoidance): Thiết kế này giúp ngăn chặn hiện tượng "bảng thưa" (bảng có quá nhiều cột bị gán giá trị NULL). Hệ thống chỉ tốn tài nguyên lưu trữ những gì thực sự cần thiết cho từng ngành hàng cụ thể. 
	Khả năng mở rộng linh hoạt (Scalability): Khi doanh nghiệp muốn mở rộng kinh doanh sang các ngành hàng mới (ví dụ: Pet Supplies, Digital Services), lập trình viên chỉ việc tạo thêm một class con mới kế thừa từ Product mà hoàn toàn không làm ảnh hưởng hay phải thay đổi cấu trúc của các bảng con hiện tại. 

2.3.3. Chi tiết theo domain 
Để quản lý các thuộc tính đặc thù của từng loại mặt hàng mà không làm bảng Product bị quá tải dữ liệu (Sparse Table), hệ thống sử dụng mô hình kế thừa thông qua quan hệ One-to-One. 
Code models.py trong product service:

```python
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name

# 10 specific product domains using multi-table inheritance
class Book(Product):
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    isbn = models.CharField(max_length=50, unique=True)
    page = models.IntegerField()
    language = models.CharField(max_length=100)

    class Meta:
        db_table = 'books'

class Electronic(Product):
    brand = models.CharField(max_length=100)
    warranty = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    power = models.CharField(max_length=100)

    class Meta:
        db_table = 'electronics'

class Fashion(Product):
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    material = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)

    class Meta:
        db_table = 'fashion'

class Cosmetic(Product):
    brand = models.CharField(max_length=100)
    skin_type = models.CharField(max_length=100)
    expiry_date = models.DateField()
    origin = models.CharField(max_length=100)

    class Meta:
        db_table = 'cosmetics'

class HealthCare(Product):
    brand = models.CharField(max_length=100)
    ingredient = models.TextField()
    expiry_date = models.DateField()
    usage = models.TextField()

    class Meta:
        db_table = 'health_care'

class Office(Product):
    brand = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=100)

    class Meta:
        db_table = 'office'

class Food(Product):
    brand = models.CharField(max_length=100)
    weight = models.CharField(max_length=50)
    expiry_date = models.DateField()
    origin = models.CharField(max_length=100)

    class Meta:
        db_table = 'food'

class Sports(Product):
    brand = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    weight = models.CharField(max_length=50)
    sport_type = models.CharField(max_length=100)

    class Meta:
        db_table = 'sports'

class Toys(Product):
    brand = models.CharField(max_length=100)
    age_range = models.CharField(max_length=50)
    material = models.CharField(max_length=100)
    player_count = models.CharField(max_length=50)

    class Meta:
        db_table = 'toys'

class HomeKitchen(Product):
    brand = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    capacity = models.CharField(max_length=50)
    warranty = models.CharField(max_length=100)

    class Meta:
        db_table = 'home_kitchen'
```

2.3.4. API 
product-service 
•GET /api/products: Lấy danh sách sản phẩm, hỗ trợ lọc theo loại, danh mục, tìm kiếm 
và phân trang. 
	POST /api/products: Tạo sản phẩm mới, payload thay đổi theo type. 
	GET /api/products/{id}: Lấy chi tiết sản phẩm theo ID, trả về dữ liệu tùy theo loại sản 
phẩm. 
	PUT /api/products/{id}: Cập nhật sản phẩm. 
	DELETE /api/products/{id}: Xóa sản phẩm. 
	GET /api/categories: Lấy danh sách danh mục. 
	POST /api/categories: Tạo danh mục mới. 

2.4. Thiết kế User Service (Django) 

2.4.1. Phân loại người dùng 
	Admin: toàn quyền hệ thống 
	Staff: xử lý đơn hàng, vận hành 
	Customer: mua hàng 

2.4.2. Class diagram 
Trong hệ thống, thực thể User đóng vai trò là Aggregate Root của User Context (hoặc Auth 
Service), chịu trách nhiệm quản lý thông tin định danh và quyền hạn của người dùng. Dựa trên 
sơ đồ thiết kế, lớp User bao gồm các thuộc tính cốt lõi sau: 
	id (int): Khóa chính (Primary Key), đóng vai trò định danh duy nhất cho mỗi tài khoản 
trong toàn hệ thống. 
	username (String) & email (String): Các thông tin định danh dùng để đăng nhập và 
liên lạc với khách hàng. Các trường này thường yêu cầu ràng buộc tính duy nhất 
(Unique) ở cấp độ cơ sở dữ liệu. 
	password (String): Mật khẩu truy cập. (Lưu ý: Mật khẩu bắt buộc phải qua các thuật toán băm (hashing) như Bcrypt hoặc Argon2 để đảm bảo an ninh). 
	role (String): Định nghĩa vai trò của người dùng (ví dụ: admin, customer, staff). Thuộc 
tính này là trụ cột để hệ thống triển khai cơ chế kiểm soát truy cập dựa trên vai trò 
(RBAC - Role-Based Access Control). 
	created_at (datetime): Dấu thời gian (Timestamp) tự động ghi nhận thời điểm tài 
khoản được khởi tạo, phục vụ cho việc kiểm toán (audit) và quản lý vòng đời tài khoản. 

2.4.3. Phân quyền (RBAC) 
	Admin: CRUD toàn bộ hệ thống 
	Staff: xử lý order, shipping 
	Customer: mua hàng, xem sản phẩm 

2.4.4. API 
	POST /api/auth/register: Đăng ký tài khoản mới. 
	POST /api/auth/login: Đăng nhập và trả về JWT access token + refresh token. 
	POST /api/auth/refresh: Làm mới access token bằng refresh token. 
	POST /api/auth/logout: Đăng xuất và blacklist refresh token. 
	GET /api/users/me: Lấy thông tin tài khoản hiện tại. 
	PUT /api/users/me: Cập nhật thông tin tài khoản. 
	POST /api/users/me/change-password: Đổi mật khẩu. 
	GET /api/users/{id}: Lấy user theo ID, dùng nội bộ giữa các service. 
	GET /api/users/me/addresses: Lấy danh sách địa chỉ giao hàng. 
	POST /api/users/me/addresses: Thêm địa chỉ mới. 
	PUT /api/users/me/addresses/{address_id}: Cập nhật địa chỉ. 
	DELETE /api/users/me/addresses/{address_id}: Xóa địa chỉ. 

2.4.5. Code models.py trong user service:
```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    class Meta:
        db_table = 'users'

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    address_line = models.CharField(max_length=500)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'addresses'
```

2.5. Thiết kế Cart Service 
 
2.5.1. Class diagram 
 
Thực thể Cart (Giỏ hàng): Gồm 3 thuộc tính (private): 
	-id : int (Khóa chính) 
	-user_id : int (Tham chiếu đến người dùng) 
	-created_at : datetime (Thời gian tạo) 
Thực thể CartItem (Chi tiết giỏ hàng): Gồm 4 thuộc tính (private): 
	-id : int (Khóa chính) 
	-cart_id : int (Khóa ngoại trỏ về Cart) 
	-product_id : int (Mã sản phẩm) 
	-quantity : int (Số lượng) 
Sơ đồ thể hiện quan hệ Composition giữa Cart và CartItem. 
	Một Cart gắn liền với một user_id. 
	CartItem chứa product_id (tham chiếu ID từ Product Service) và số lượng. 

2.5.2. Logic 
Dựa trên thiết kế, module Giỏ hàng (Cart Context) sẽ đảm nhận các luồng xử lý logic cốt lõi 
sau: 
Thêm mới và Cộng dồn (Add/Increment): Khi người dùng thao tác thêm sản phẩm, 
hệ thống sẽ kiểm tra sự tồn tại của product_id trong Cart hiện tại. Nếu mặt hàng chưa 
có, tạo mới một bản ghi CartItem. Nếu đã tồn tại, tự động cộng dồn số lượng hiện tại 
với số lượng vừa thêm. 
Cập nhật số lượng chủ động (Update Quantity): Cho phép người dùng thay đổi 
trực tiếp và chính xác số lượng của một mặt hàng (ví dụ: sửa số lượng từ 2 thành 5). 
Ràng buộc: Hệ thống phải kiểm tra, nếu số lượng truyền vào bằng 0 (hoặc âm), sẽ tự 
động kích hoạt luồng xóa sản phẩm đó khỏi giỏ. 
Quản lý loại bỏ (Remove/Clear): Hỗ trợ dọn dẹp giỏ hàng theo hai cấp độ: gỡ bỏ lẻ 
từng mặt hàng (xóa CartItem cụ thể) hoặc dọn sạch toàn bộ (xóa tất cả CartItem đang 
có nhưng vẫn giữ lại thực thể Cart gốc của user để tái sử dụng). 
Đồng bộ và Tính toán (Checkout Preview): Đây là bước đệm quan trọng trước khi 
tạo đơn hàng. Giỏ hàng chỉ lưu product_id and quantity. Do đó, logic xem trước yêu 
cầu Cart Service phải giao tiếp (gọi API) sang Product Service để lấy thông tin giá 
(price) mới nhất ngay tại thời điểm hiện tại. Từ đó, tiến hành nhân đơn giá với số 
lượng, cộng tổng để trả về con số tạm tính (Subtotal) và tổng tiền (Total) cho người 
dùng. 

2.5.3. API 
	GET /api/cart: Lấy giỏ hàng của user hiện tại. 
	DELETE /api/cart: Xóa toàn bộ giỏ hàng. 
	POST /api/cart/items: Thêm sản phẩm vào giỏ, nếu đã có thì cộng thêm số lượng. 
	PUT /api/cart/items/{product_id}: Cập nhật số lượng sản phẩm trong giỏ. 
	DELETE /api/cart/items/{product_id}: Xóa một sản phẩm khỏi giỏ. 
	GET /api/cart/checkout-preview: Xem trước đơn hàng trước khi checkout, tính tổng 
tiền. 

2.5.4. Code models.py trong cart service:
```python
from django.db import models

class Cart(models.Model):
    user_id = models.IntegerField(unique=True)  # Logic reference to User Service (PostgreSQL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'carts'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()  # Logic reference to Product Service (PostgreSQL)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'product_id')
```

2.6. Thiết kế Order Service 
 
2.6.1. Class diagram 
 
Sơ đồ áp dụng quan hệ Composition giữa thực thể Order và OrderItem, trong đó Order đóng 
vai trò là Aggregate Root. 
	Thực thể Order: Gắn liền với user_id, lưu trữ tổng giá trị đơn hàng (total_price), trạng 
thái hiện tại (status - ví dụ: Pending, Processing, Shipped, Cancelled) và thời gian tạo. 
	Thực thể OrderItem: Chứa chi tiết các mặt hàng trong đơn. 
	Điểm khác biệt then chốt so với CartItem: Lớp OrderItem có thêm thuộc tính -price 
: float. Đây là thiết kế bắt buộc trong E-commerce (Lưu vết giá - Price Snapshot). Giá 
của sản phẩm có thể thay đổi trong tương lai, nhưng giá ghi nhận trong OrderItem là cố 
định tại thời điểm khách hàng chốt đơn, đảm bảo tính toàn vẹn của lịch sử giao dịch. 

2.6.2. Workflow 
•User tạo đơn qua POST /api/orders; hệ thống tạo Order với trạng thái pending và 
các OrderItem con. 
•User xem danh sách, xem chi tiết, hoặc hủy đơn; hủy chỉ cho phép khi đơn còn pending. 
•Khi thanh toán thành công, payment-service cập nhật Payment sang success và gọi 
ngược sang order-service để đẩy trạng thái đơn sang processing. 
•Sau đó shipping-service tạo shipment cho order_id, trạng thái ban đầu là pending, rồi 
cập nhật dần sang picked_up, in_transit, delivered, v.v. 

2.6.3. API 
POST /api/orders: Tạo đơn hàng. 
GET /api/orders: Lấy danh sách đơn hàng của user hiện tại, có lọc theo status và phân 
trang. 
GET /api/orders/{id}: Lấy chi tiết đơn hàng. 
DELETE /api/orders/{id}: Hủy đơn hàng, chỉ áp dụng khi status là pending. 
PUT /api/orders/{id}/status: Cập nhật trạng thái đơn hàng, dùng cho admin hoặc 
internal service. 
GET /api/orders/admin/list: Lấy danh sách tất cả đơn hàng cho admin, có lọc user_id, 
status và phân trang. 

2.6.4. Code models.py trong order service:
```python
from django.db import models

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    user_id = models.IntegerField()  # Logic reference to User Service (PostgreSQL)
    total_price = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()  # Logic reference to Product Service (PostgreSQL)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=14, decimal_places=2)  # Price snapshot

    class Meta:
        db_table = 'order_items'
```

2.7. Thiết kế Payment Service 

2.7.1. Class diagram 
 
Sơ đồ thể hiện cấu trúc của thực thể Payment, đóng vai trò là Aggregate Root trong Bounded 
Context về thanh toán. Thực thể này hoạt động độc lập và liên kết với Đơn hàng thông qua ID. 
id : int: Định danh duy nhất của giao dịch thanh toán. 
order_id : int: Khóa ngoại tham chiếu đến Đơn hàng (Order) cần thanh toán. Việc chỉ 
lưu order_id giúp Payment Service không bị phụ thuộc chặt chẽ vào cấu trúc dữ liệu 
của Order Service (Loose Coupling). 
amount : double: Số tiền giao dịch thực tế. 
status : String: Trạng thái của giao dịch (ví dụ: Pending, Success, Failed) 
method : String: Phương thức thanh toán được người dùng lựa chọn 
created_at : datetime: Thời gian khởi tạo giao dịch. 

2.7.2. Workflow 
POST /api/payments: tạo payment mới từ order_id, amount, method; bản ghi mới được 
tạo với trạng thái ban đầu là pending. 
GET /api/payments/{id}: xem chi tiết một giao dịch thanh toán. 
POST /api/payments/{id}/confirm: mô phỏng callback xác nhận thanh toán; nhận status 
success, failed, hoặc processing và cập nhật payment.status. 
Khi status là success, service gọi sang order-service để đổi trạng thái đơn sang 
processing. 
GET /api/payments/order/{order_id}: lấy payment gần nhất theo order_id 

2.7.3. API 
	POST /api/payments: Tạo giao dịch thanh toán cho một đơn hàng. 
	GET /api/payments/{id}: Lấy chi tiết giao dịch thanh toán. 
	POST /api/payments/{id}/confirm: Xác nhận thanh toán theo callback mock webhook. 
	GET /api/payments/order/{order_id}: Lấy thông tin thanh toán theo order_id. 

2.7.4. Code models.py trong payment service:
```python
from django.db import models

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    METHOD_CHOICES = (
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash on Delivery (COD)'),
        ('e_wallet', 'E-Wallet'),
    )
    order_id = models.IntegerField()  # Logic reference to Order Service (PostgreSQL)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
```

2.8. Thiết kế Shipping Service 

2.8.1. Class diagram 
 
Sơ đồ thể hiện cấu trúc của thực thể Shipment, đóng vai trò là Aggregate Root trong Bounded 
Context về logistics và vận chuyển. Tương tự như Payment, Shipping Service hoạt động độc 
lập và chỉ tham chiếu đến Đơn hàng thông qua ID. 
id : int: Định danh duy nhất của vận đơn. 
order_id : int: Khóa ngoại tham chiếu đến Đơn hàng (Order). Đảm bảo tính độc lập 
(Loose Coupling) giữa Shipping Service và Order Service 
address : String: Địa chỉ giao hàng chi tiết của người mua 
status : String: Trạng thái vận chuyển hiện tại 
shipped_at : datetime: Dấu thời gian ghi nhận lúc đối tác vận chuyển lấy hàng đi 
delivered_at : datetime: Dấu thời gian ghi nhận lúc khách hàng thực tế nhận được bưu 
kiện 

2.8.2. Trạng thái 
	Processing 
	Shipping 
	Delivered 

2.8.3. API 
	POST /api/shipments: Tạo thông tin vận chuyển cho đơn hàng. 
	GET /api/shipments/{id}: Lấy chi tiết vận chuyển. 
	PUT /api/shipments/{id}/status: Cập nhật trạng thái vận chuyển. 
	GET /api/shipments/order/{order_id}: Lấy thông tin vận chuyển theo order_id. 

2.8.4. Code models.py trong shipping service:
```python
from django.db import models

class Shipment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    )
    order_id = models.IntegerField()  # Logic reference to Order Service (PostgreSQL)
    address = models.CharField(max_length=500)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'shipments'
```

2.9. Luồng hệ thống tổng thể 
Hệ thống vận hành dựa trên cơ chế giao tiếp liên dịch vụ (Inter-service communication) thông 
qua REST API, đảm bảo tính độc lập của từng Bounded Context. 
1. Luồng Đăng ký & Định danh (Identity Flow) 
	User Service: Người dùng đăng ký tài khoản và đăng nhập. Hệ thống trả về một mã 
định danh (JWT Token) chứa user_id và role. 
	Các Service khác (Cart, Order) sẽ sử dụng user_id này để định danh chủ sở hữu dữ liệu 
mà không cần truy vấn lại bảng User của PostgreSQL. 
2. Luồng Mua sắm & Giỏ hàng (Shopping Flow) 
	Product Service: Người dùng xem danh sách sản phẩm (Books, Fashion, Electronics, 
Cosmetic). 
	Cart Service: Khi khách hàng nhấn "Thêm vào giỏ", Cart Service sẽ nhận product_id. 
Nó có thể thực hiện một lệnh gọi API (gọi là Synchronous Call) sang Product Service
để kiểm tra xem sản phẩm đó có còn tồn kho (stock > 0) hay không trước khi lưu vào 
bảng CartItem. 
3. Luồng Đặt hàng & Thanh toán (Checkout Flow) 
Đây là luồng quan trọng nhất thể hiện sự phối hợp giữa các Package: 
	Bước 1 (Order Creation): Người dùng nhấn "Đặt hàng", Order Service sẽ lấy dữ liệu 
từ Cart Service, tính toán total_price và tạo bản ghi trong bảng Order & OrderItem. 
	Bước 2 (Payment): Sau khi có order_id, Payment Service sẽ tiếp nhận yêu cầu thanh 
toán. Sau khi người dùng thanh toán thành công, trạng thái đơn hàng trong Order 
Service sẽ được cập nhật thành Paid. 
4. Luồng Giao hàng (Fulfilment Flow) 
	Shipping Service: Ngay sau khi đơn hàng chuyển sang trạng thái đã thanh toán, 
Shipping Service sẽ lấy thông tin địa chỉ và danh sách sản phẩm từ Order Service để 
tạo đơn vận chuyển (Shipment). 
	Quá trình giao hàng sẽ cập nhật trạng thái từ Processing → Shipping → Delivered. 

2.9.1 Sơ đồ gói thể hiện luồng hoạt động của hệ thống 
 
Bảng tóm tắt tương tác giữa các Service 
Điểm bắt đầu 	Gọi đến Service 	Mục đích 
Cart Service 	Product Service 	Lấy tên, giá và dữ liệu sản phẩm để hiển thị giỏ hàng, tính tổng tiền. 
Gateway Service 	Product Service 	Lấy danh sách, chi tiết, danh mục và tìm kiếm sản phẩm cho UI. 
Gateway Service 	Cart Service 	Lấy giỏ hàng hiện tại trước checkout. 
Gateway Service 	Order Service 	Tạo đơn từ cart, xem danh sách và chi tiết đơn. 
Gateway Service 	Payment Service 	Tạo payment cho order và xem lịch sử thanh toán. 
Gateway Service 	Shipping Service 	Tạo shipment cho order và xem lịch sử vận chuyển. 
Payment Service 	Order Service 	Khi confirm success thì đổi trạng thái order sang processing. 
Order Service 	Không có gọi HTTP trực tiếp 	Chỉ xác thực JWT và lấy thông tin user từ token. 
Shipping Service 	Không có gọi HTTP trực tiếp 	Chỉ tạo và cập nhật shipment theo order_id. 

2.9.2. Mapping Class Diagram sang DB Schema 
Hệ thống được thiết kế theo kiến trúc Microservices, do đó mỗi Package trong sơ đồ Class sẽ 
tương ứng với một cơ sở dữ liệu riêng biệt. 
1. Product Service (PostgreSQL) 
Mô tả: Sử dụng mô hình kế thừa Table-per-Type (Multi-Table Inheritance) để quản lý đa dạng 
sản phẩm. 
Class 	Table Name 	Key Mapping 	Ghi chú 
Category	categories 	id (PK) 	Lưu trữ danh mục sản phẩm (Electronics, Books, Cosmetics, Fashion, Home & Kitchen, Sports, Toys, Food, Health Care, Office). 
Product	products 	id (PK) category_id (FK → categories.id) 	Bảng chứa thông tin chung: name, price, stock, description. 
Book	books 	product_id (PK, FK → products.id) 	Nối 1-1 với products.id. Thuộc tính: author, publisher, isbn, page, language. 
Electronic	electronics 	product_id (PK, FK → products.id) 	Nối 1-1 với products.id. Thuộc tính: brand, warranty, model, power. 
Fashion	fashion 	product_id (PK, FK → products.id) 	Nối 1-1 với products.id. Thuộc tính: size, color, material, gender. 
Cosmetic	cosmetics 	product_id (PK, FK → products.id) 	Nối 1-1 với products.id. Thuộc tính: brand, skin_type, expiry_date, origin. 
HomeKitchen	home_kitchen 	product_id (PK, FK → products.id) 	Nối 1-1 với products.id. Thuộc tính: brand, material, capacity, warranty. 
Sports	sports 	product_id (PK, FK → products.id) 	Nối 1-1 với products.id. Thuộc tính: brand, size, weight, sport_type. 
Toys	toys 	product_id (PK, FK → products.id) 	Nối 1-1 với products.id. Thuộc tính: brand, age_range, material, player_count. 
Food	food 	product_id (PK, FK → products.id) 	Nối 1-1 với products.id. Thuộc tính: brand, weight, expiry_date, origin. 
HealthCare	health_care 	product_id (PK, FK → products.id) 	Nối 1-1 với products.id. Thuộc tính: brand, ingredient, expiry_date, usage. 
Office	office 	product_id (PK, FK → products.id) 	Nối 1-1 với products.id. Thuộc tính: brand, material, color, size. 

Đặc điểm kế thừa: 
	Multi-Table Inheritance: Mỗi loại sản phẩm có bảng riêng, kế thừa từ products. 
	Quan hệ 1-1: product_id trong bảng con là PK và FK đồng thời. 
	Cascade Delete: Xóa product → tự động xóa record trong bảng con. 
	Django ORM: Tự động JOIN khi query model con (vd: Book.objects.get(id=1) → JOIN products + books). 

2. User Service (PostgreSQL) 
Mô tả: Quản lý người dùng và phân quyền bằng PostgreSQL. 
Class 	Table Name 	Attribute Mapping 	Ghi chú 
User	users 	id (PK, SERIAL) username (VARCHAR(150), UNIQUE) password (VARCHAR(255)) email (VARCHAR(255), UNIQUE) role (VARCHAR(10)) created_at (TIMESTAMP) 	- Lưu username, password (hashed với Django PBKDF2/bcrypt). 
- role: 'admin', 'staff', 'customer'. 
- Password được hash bằng make_password(). 
Lưu ý: 
	Không có bảng riêng cho Customer/Admin (sử dụng field role để phân biệt). 
	Email và username đều UNIQUE để tránh trùng lặp. 
	created_at tự động set khi tạo user mới (auto_now_add=True). 

3. Cart Service (PostgreSQL) 
Mô tả: Lưu trữ trạng thái mua sắm tạm thời bằng PostgreSQL. 
Class 	Table Name 	Logic Link 	Ghi chú 
Cart	carts 	id (PK, SERIAL) user_id (INT, UNIQUE) created_at (TIMESTAMP) 	- Tham chiếu logic sang User Service (user_id). 
- Mỗi user chỉ có 1 cart (UNIQUE constraint). 
CartItem	cart_items 	id (PK, SERIAL) cart_id (FK → carts.id) product_id (INT) quantity (INT, default=1) 	- Tham chiếu logic sang Product Service (product_id). 
- Quan hệ N-1 với Cart (1 cart có nhiều items). 
- Cascade delete: Xóa cart → xóa tất cả cart_items. 
Lưu ý: 
	user_id không phải FK thực (vì khác database) → Logic reference only. 
	product_id không phải FK thực (vì khác database) → Logic reference only. 
	Khi user thêm sản phẩm vào giỏ, kiểm tra product tồn tại qua API call đến Product Service. 

4. Order Service (PostgreSQL) 
Mô tả: Quản lý giao dịch và lịch sử mua hàng. 
Class 	Table Name 	Attribute Mapping 	Ghi chú 
Order	orders 	id (PK, SERIAL) user_id (INT) total_price (DECIMAL(14,2)) status (VARCHAR(50), default='pending') created_at (TIMESTAMP) 	- Lưu tổng tiền và trạng thái đơn. 
- status: 'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'. 
- user_id: Tham chiếu logic sang User Service. 
OrderItem	order_items 	id (PK, SERIAL) order_id (FK → orders.id) product_id (INT) quantity (INT) price (DECIMAL(14,2)) 	- Quan trọng: Lưu giá tại thời điểm mua (Snapshot). 
- price: Giá sản phẩm tại lúc đặt hàng. 
- Cascade delete: Xóa order → xóa tất cả order_items. 
Lưu ý: 
	Price Snapshot: OrderItem.price lưu giá tại thời điểm mua, không phải giá hiện tại trong Product Service. 
	Immutable: Sau khi tạo order, không được sửa price (đảm bảo tính toàn vẹn lịch sử). 
	Status workflow: pending → confirmed → processing → shipped → delivered/cancelled. 

5. Payment Service (PostgreSQL) 
Mô tả: Quản lý thanh toán. 
Class 	Table Name 	Logic Link 	Ghi chú 
Payment	payments 	id (PK, SERIAL) order_id (INT) amount (DECIMAL(14,2)) status (VARCHAR(50), default='pending') method (VARCHAR(50)) created_at (TIMESTAMP) 	- Lưu số tiền thanh toán thực tế. 
- order_id: Tham chiếu logic sang Order Service. 
- status: 'pending', 'success', 'failed'. 
- method: 'card', 'bank_transfer', 'cash', 'e_wallet'. 
Lưu ý: 
	amount có thể khác Order.total_price (do giảm giá, phí phát sinh, etc.). 
	Mỗi order có thể có nhiều payment records (thanh toán nhiều lần, hoàn tiền, etc.). 
	status được cập nhật sau khi payment gateway trả response. 

6. Shipping Service (PostgreSQL) 
Mô tả: Quản lý vận chuyển bằng PostgreSQL. 
Class 	Table Name 	Logic Link 	Ghi chú 
Shipment	shipments 	id (PK, SERIAL) order_id (INT) tracking_number (VARCHAR(100), nullable) status (VARCHAR(50), default='pending') address (VARCHAR(500)) shipped_at (TIMESTAMP, nullable) delivered_at (TIMESTAMP, nullable) estimated_delivery (DATE, nullable) 	- Lưu địa chỉ và trạng thái vận chuyển. 
- order_id: Tham chiếu logic sang Order Service. 
- status: 'pending', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'failed'. 
- tracking_number: Mã vận đơn (do đối tác vận chuyển cấp). 
Lưu ý: 
	Mỗi order có thể có nhiều shipment records. 
	estimated_delivery được tính dựa trên địa chỉ và phương thức vận chuyển. 
	tracking_number nullable vì chỉ có khi đối tác vận chuyển xác nhận nhận hàng. 

7. AI Service (PostgreSQL) 
Mô tả: Quản lý dữ liệu AI, embeddings, và user behaviors. 
Class 	Table Name 	Attribute Mapping 	Ghi chú 
UserBehavior	ai_user_behaviors 	id (PK, SERIAL) user_id (INT) product_id (INT) action_type (VARCHAR(20)) timestamp (TIMESTAMP) 	- Lưu hành vi người dùng để training model. 
- action_type: 'view', 'add_to_cart', 'purchase', 'rate', 'search'. 
user_id, product_id: Tham chiếu logic sang User/Product Service. 
Vector Databases (External): 
	ChromaDB: Lưu embeddings cho semantic search. 
	Neo4j: Lưu knowledge graph cho RAG. 
Lưu ý: 
	ChromaDB và Neo4j không phải relational databases → Không có FK constraints. 
	ai_user_behaviors dùng để train recommendation models (RNN/LSTM/BiLSTM). 
	Data pipeline: PostgreSQL → Training data → Model weights (.h5, .tflite files). 

> [!IMPORTANT]
> **Lưu ý phát triển (Development Note)**: Phần huấn luyện mô hình AI (Model Training cho các thuật toán RNN/LSTM/BiLSTM) cũng như tích hợp chi tiết các cơ sở dữ liệu Vector (ChromaDB, Neo4j) phục vụ tìm kiếm ngữ nghĩa và RAG Chatbot được lên kế hoạch thực hiện ở giai đoạn sau của dự án. Trong giai đoạn hiện tại, hệ thống tập trung xây dựng cơ sở hạ tầng lưu trữ hành vi người dùng (`ai_user_behaviors`) để chuẩn bị sẵn sàng dữ liệu cho quá trình huấn luyện sau này.

8. Gateway Service (PostgreSQL) 
Mô tả: Lưu trữ thông tin customer cho gateway (tách biệt với User Service). 
Class 	Table Name 	Attribute Mapping 	Ghi chú 
Customer	gateway_customers 	id (PK, SERIAL) full_name (VARCHAR(255)) email (VARCHAR(255), UNIQUE) phone (VARCHAR(50)) address (VARCHAR(500)) created_at (TIMESTAMP) 	Lưu thông tin khách hàng cho gateway UI. Khác với users table trong User Service. Email là identifier chung giữa gateway và user-service. 

2.9.3. Thiết kế Database cho từng Service 
Nguyên tắc Microservices:
	Mỗi service có database riêng 
	Không share database giữa các service 

1. Product Service (PostgreSQL) 
Lý do chọn:
	Hỗ trợ cực tốt kiểu dữ liệu JSONB để lưu thông tin động của sản phẩm. 
	Hỗ trợ toàn vẹn dữ liệu và quan hệ phức tạp (ACID Compliance). 
	Khả năng tương thích hoàn hảo với Django ORM cho cơ chế Multi-table Inheritance. 
	Tích hợp bộ công cụ Tìm kiếm toàn văn (Full-Text Search). 

2. User Service (PostgreSQL) [Đã chuyển từ MySQL]
Lý do chọn:
	Đảm bảo độ tin cậy và tính toàn vẹn (ACID) cao nhất cho dữ liệu định danh người dùng.
	Đồng bộ hóa công nghệ cơ sở dữ liệu trên toàn hệ thống giúp giảm thiểu chi phí quản lý vận hành.
	Hỗ trợ bảo mật cao và các tính năng mã hóa, phân quyền tích hợp.

3. Payment Service (PostgreSQL) 
Yêu cầu tính nhất quán dữ liệu (ACID) cực cao để tránh mất mát tiền bạc hoặc sai lệch số dư. 

4. Order Service (PostgreSQL) 
Lý do: Đảm bảo tính toàn vẹn dữ liệu (ACID) cực kỳ tốt cho các giao dịch tài chính mua bán và ghi vết đơn hàng. 

5. Shipping Service (PostgreSQL) [Đã chuyển từ MySQL]
Lý do chọn:
	Hỗ trợ thư viện PostGIS rất mạnh mẽ để lập chỉ mục địa lý, tính toán khoảng cách và tối ưu tuyến đường giao hàng.
	Đảm bảo tính nhất quán dữ liệu cao trong các giao dịch đồng thời cập nhật trạng thái vận đơn.

6. Cart Service (PostgreSQL) [Đã chuyển từ MySQL]
Lý do chọn:
	Tận dụng trường JSONB để lưu trữ các trạng thái giỏ hàng tùy biến, tạm thời mà không cần xây dựng hệ quản trị quan hệ phức tạp.
	Giúp việc lưu vết thông tin giỏ hàng đạt hiệu năng cao và đồng bộ công nghệ với toàn hệ thống.

2.9.4. So sánh MySQL vs PostgreSQL 
*Chú thích: Hệ thống đã quyết định sử dụng PostgreSQL làm hệ quản trị cơ sở dữ liệu duy nhất cho tất cả các microservices để chuẩn hóa hạ tầng, giảm chi phí vận hành và tối ưu hóa việc mở rộng hệ thống.*

Tiêu chí 	MySQL 	PostgreSQL 
Kiến trúc cốt lõi 	Hệ quản trị cơ sở dữ liệu quan hệ (RDBMS) truyền thống, tập trung vào tốc độ và sự đơn giản. 	Hệ quản trị cơ sở dữ liệu đối tượng - quan hệ (ORDBMS), tập trung vào tính năng nâng cao và chuẩn tắc. 
Hiệu năng tổng quan 	Cực nhanh với các tác vụ Đọc nặng (Read-heavy) và các câu truy vấn đơn giản nhờ cơ chế tối ưu hóa bộ nhớ đệm tốt. 	Vượt trội với các tác vụ hỗn hợp (Đọc/Ghi phức tạp), xử lý dữ liệu quy mô lớn và các câu lệnh phân tích dữ liệu chuyên sâu. 
Hỗ trợ JSON 	Trung bình: Hỗ trợ từ bản 5.7 nhưng cú pháp truy vấn phức tạp hơn, lập chỉ mục (Index) phải qua cơ chế cột ảo (Virtual Columns). 	Mạnh mẽ: Hỗ trợ kiểu JSONB (định dạng nhị phân), cho phép lập chỉ mục GIN Index giúp tìm kiếm sâu vào bên trong Object với tốc độ cực nhanh. 
Xử lý quan hệ phức tạp 	Trung bình: Tốc độ giảm rõ rệt khi thực hiện các câu lệnh JOIN quá nhiều bảng hoặc xử lý các tầng dữ liệu lồng nhau. 	Tốt: Bộ tối ưu hóa truy vấn (Query Optimizer) rất thông minh, hỗ trợ xuất sắc các phép toán phức tạp, truy vấn đệ quy và CTE (Common Table Expressions). 
Kế thừa dữ liệu 	Không hỗ trợ ở mức database. Nếu làm kế thừa (như Multi-table Inheritance) phải cấu hình hoàn toàn bằng tay thông qua quan hệ 1-1 ở tầng ORM. 	Hỗ trợ Kế thừa bảng (Table Inheritance) trực tiếp ở mức cơ sở dữ liệu, cho phép bảng con tự động kế thừa cấu trúc của bảng cha. 
Mở rộng cho AI & RAG 	Hạn chế: Không có các extension mã nguồn mở chính thức và đủ mạnh mẽ để xử lý Vector dữ liệu cho các mô hình AI. 	Mạnh mẽ: Hỗ trợ extension pgvector, cho phép lưu trữ và tìm kiếm khoảng cách giữa các Vector Embeddings trực tiếp bằng SQL cho ứng dụng RAG. 
Tìm kiếm toàn văn 	Có hỗ trợ cơ bản trên công cụ InnoDB và MyISAM, đáp ứng tốt các nhu cầu tìm kiếm từ khóa đơn giản. 	Tích hợp bộ công cụ tìm kiếm chuyên sâu (tsvector, tsquery) hỗ trợ bóc tách từ, từ dừng (stop-words), tiệm cận năng lực của Elasticsearch. 
Kiểm soát đồng thời 	Sử dụng cơ chế khóa dòng (Row-level locking) thông qua bộ máy InnoDB. 	Sử dụng công nghệ MVCC (Multi-Version Concurrency Control) nâng cao, giúp tác vụ Đọc và Ghi không bao giờ block (khóa) lẫn nhau. 
Khả năng mở rộng 	Rất mạnh về Read-Scaling nhờ mô hình sao chép Master-Slave Replication chín muồi và dễ cấu hình. 	Mạnh về cả Read và Write-Scaling, hỗ trợ phân mảnh dữ liệu (Partitioning) nâng cao ở quy mô hàng trăm triệu dòng dữ liệu. 

2.10. Kết luận 
Chương 2 đã trình bày chi tiết quá trình phân tích và thiết kế hệ thống E-commerce theo kiến trúc Microservices. Qua đó, các mục tiêu quan trọng về mặt kỹ thuật đã được hiện thực hóa: 
	Tối ưu hóa kiến trúc với DDD: Việc áp dụng thiết kế hướng tên miền (Domain-Driven Design) đã giúp phân tách hệ thống thành các Bounded Context rõ ràng. Điều này không chỉ giúp quản lý mã nguồn dễ dàng mà còn đảm bảo tính độc lập cao giữa các nghiệp vụ như Product, Order, và User. 
	Chuẩn hóa và đồng bộ hóa công nghệ Database: Toàn bộ hệ thống được thống nhất sử dụng PostgreSQL cho tất cả các microservices. Điều này giúp tối ưu hóa việc quản lý vận hành, bảo mật và sao lưu dữ liệu, đồng thời cho phép các dịch vụ tận dụng tối đa các tính năng nâng cao (như JSONB cho Cart/Product, pgvector cho AI, và PostGIS cho Shipping). Việc áp dụng quy tắc "Database per Service" với duy nhất một loại RDBMS làm giảm độ phức tạp vận hành của hạ tầng.
	Django và khả năng phát triển nhanh: Việc sử dụng framework Django cho phép chuyển đổi nhanh chóng từ sơ đồ lớp (Class Diagram) sang các Model và Database Schema thực tế. Các mối quan hệ kế thừa (Table-per-Type) trong Product Service đã được giải quyết triệt để, đáp ứng tốt yêu cầu quản lý đa domain sản phẩm. 
	Sẵn sàng cho việc mở rộng: Với thiết kế ghép nối lỏng (Loose Coupling) thông qua các Logical Foreign Keys, hệ thống đã sẵn sàng để triển khai các bước tiếp theo như xây dựng API Gateway, triển khai Docker và thiết lập giao tiếp liên dịch vụ (Inter-service communication). 
Nhìn chung, cấu trúc hệ thống ở Chương 2 đã tạo nên một nền tảng vững chắc, đúng tiêu chuẩn hiện đại, giúp việc triển khai code backend ở các chương sau trở nên minh bạch và nhất quán. 

---

## 2.11. Ke hoach mo rong Admin/Staff/Shipper va UI theo role

Chi tiet ke hoach mo rong frontend, backend, database va pending tasks da duoc tach sang file `plan_roles_frontend_backend_db.md` de tranh loi encoding trong `plan.md` hien tai.

Trang thai: PENDING.

Pham vi can lam tiep:
- Them role `shipper` va admin user APIs.
- Them dashboard frontend theo role: customer, admin, staff, shipper.
- Them admin/staff backend APIs cho products, orders, payments, shipments.
- Them shipper backend APIs de xem shipment duoc gan va cap nhat trang thai giao hang.
- Mo rong DB cho `Order` va `Shipment` de luu assigned staff/shipper va delivery notes.
- Khong can JWT trong giai do nay; dung role + `X-User-Id`/`X-User-Role` de phan quyen nhanh.
- Them integration test `test_admin_staff_shipper_flow.py`.
