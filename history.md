# Lịch sử và Tiến độ dự án Microservices E-Commerce

Tài liệu này ghi nhận toàn bộ lịch sử thiết kế, triển khai cơ sở hạ tầng, mã nguồn các dịch vụ và tiến độ kiểm thử tích hợp của hệ thống.

---

## 1. Cơ cấu cổng dịch vụ (Port Mapping) & Cơ sở dữ liệu (PostgreSQL)

Hệ thống bao gồm 8 microservices chạy độc lập trên local thông qua môi trường ảo `.venv` và kết nối tới container PostgreSQL trên Docker Desktop qua port host **5435** (để tránh xung đột với cổng 5432 của dịch vụ PostgreSQL gốc trên Windows).

| Service | Port | Database Name | Chức năng chính | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| `user-service` | `8001` | `user_db` | Quản lý User (Admin, Customer, Staff) và Addresses | **Hoàn thành** |
| `product-service` | `8002` | `product_db` | Quản lý danh mục & 10 lớp sản phẩm kế thừa | **Hoàn thành** |
| `cart-service` | `8003` | `cart_db` | Quản lý giỏ hàng tạm thời, kết nối kiểm tra stock | **Hoàn thành** |
| `order-service` | `8004` | `order_db` | Xử lý đơn hàng, chụp ảnh giá sản phẩm | **Hoàn thành** |
| `payment-service` | `8005` | `payment_db` | Mô phỏng cổng thanh toán & xác nhận webhook | **Hoàn thành** |
| `shipping-service` | `8006` | `shipping_db` | Tạo vận đơn giao hàng, tự cập nhật hoàn thành đơn | **Hoàn thành** |
| `ai-service` | `8007` | `ai_db` | Lưu vết hành vi người dùng (`UserBehavior`) | **Hoàn thành** |
| `gateway-service` | `8008` | `gateway_db` | API Gateway lưu thông tin Customer cấu hình | **Hoàn thành** |

---

## 2. Nhật ký Triển khai (Implementation History)

### Phase 1: Infrastructure & DB Setup (Hoàn thành)
- Tạo [docker-compose.yml](file:///d:/2026/thayque/tieuluan/docker-compose.yml) cấu hình PostgreSQL container map port `5435 -> 5432`.
- Thiết lập kịch bản SQL khởi tạo tự động tạo 8 databases tương ứng.
- Tạo môi trường ảo Python `.venv`, cài đặt các thư viện cần thiết (`django`, `djangorestframework`, `psycopg2`, `requests`).
- Chạy script tự động sinh 8 boilerplate Django project.

### Phase 2: Core Services (Hoàn thành)
- **User Service (`8001`)**: Triển khai các API Đăng ký, Đăng nhập (bỏ qua JWT để chạy local đơn giản), Quản lý địa chỉ (`Address`). Đã chạy migration thành công.
- **Product Service (`8002`)**: Triển khai thiết kế kế thừa đa bảng (Multi-table Inheritance) cho 10 domain sản phẩm khác nhau. Xây dựng các Serializers đa hình (Polymorphic) và API CRUD sản phẩm. Đã chạy migration thành công.

### Phase 3: Transactional Services (Hoàn thành)
- **Cart Service (`8003`)**: Quản lý giỏ hàng (`Cart`, `CartItem`). Tích hợp gọi đồng bộ (Synchronous HTTP) sang Product Service để kiểm tra tồn kho khi thêm/sửa giỏ hàng. Đã chạy migration thành công.
- **Order Service (`8004`)**: Xử lý tạo đơn hàng từ giỏ hàng, chụp ảnh địa chỉ giao hàng và giá sản phẩm tại thời điểm mua, trừ số lượng tồn kho sản phẩm tương ứng. Đã chạy migration thành công.

### Phase 4: Fulfilment Services (Hoàn thành)
- **Payment Service (`8005`)**: Mô phỏng tạo giao dịch thanh toán và webhook xác nhận thành công/thất bại để cập nhật trạng thái đơn hàng. Đã chạy migration thành công.
- **Shipping Service (`8006`)**: Tự động tạo vận đơn khi thanh toán thành công. Khi vận đơn chuyển sang trạng thái "Đã giao hàng" (delivered), tự động gọi Order Service cập nhật đơn hàng thành "Hoàn thành" (completed). Đã chạy migration thành công.

### Phase 5: Support Services, Seeding & Testing (Hoàn thành)
- **AI Service (`8007`)**: Cung cấp API ghi nhận hành vi xem, thêm giỏ hàng, mua hàng của người dùng. Đã chạy migration thành công.
- **Gateway Service (`8008`)**: Cung cấp API quản lý thông tin khách hàng giao tiếp hệ thống. Đã chạy migration thành công.
- **Data Seeding (`seed_data.py`)**: Script nạp dữ liệu mẫu bao gồm tài khoản khách hàng, quản trị viên, các địa chỉ mẫu, danh mục và các sản phẩm chuyên biệt của 10 domain (Sách, Laptop, Áo khoác...).
- **Multi-service Runner (`run_all.ps1`)**: Script PowerShell khởi động đồng thời cả 8 microservices ở chế độ nền (background) và chuyển hướng log chi tiết vào thư mục `logs/` độc lập.

---

## 3. Trạng thái Kiểm thử Tích hợp (Integration Testing Status)

Kịch bản kiểm thử tích hợp [test_flow.py](file:///d:/2026/thayque/tieuluan/test_flow.py) mô phỏng toàn bộ hành trình mua sắm của một khách hàng:
1. Đăng nhập hệ thống.
2. Lấy danh sách sản phẩm mẫu.
3. Thêm sản phẩm vào giỏ hàng.
4. Xem trước giỏ hàng và tổng tiền.
5. Lấy địa chỉ giao hàng mặc định.
6. Gửi yêu cầu đặt hàng (Order Service).
7. Tạo giao dịch thanh toán (Payment Service).
8. Xác nhận thanh toán thành công (Webhook).
9. Tạo vận đơn giao hàng và cập nhật hành trình giao (Shipping Service).
10. Ghi nhận hành vi mua sắm vào dịch vụ AI (AI Service).

**Tiến độ hiện tại**:
- Hệ thống đã sẵn sàng và chạy tốt các API độc lập.
- Khi tích hợp chuỗi gọi API đồng bộ ở bước tạo đơn hàng (`order-service` -> `cart-service` -> `product-service`), đã xảy ra hiện tượng phản hồi chậm (Read Timeout) do độ trễ kết nối lần đầu (cold start) giữa các Django development server đơn luồng.
- **Giải pháp đang thực hiện**: Tối ưu hóa cấu hình gọi API và kiểm tra kỹ cơ chế xử lý đồng thời của các tiến trình dịch vụ.

### Cap nhat 2026-06-12 20:20
- Da chay lai `test_flow.py` bang `.venv\Scripts\python.exe`; integration test end-to-end hoan thanh thanh cong toan bo 16 buoc.
- Cac buoc da xac nhan: login, lay catalog, them gio hang, checkout preview, tao order, tru stock, tao va confirm payment, tao shipment, giao hang, cap nhat order `completed`, ghi behavior AI va doc metadata gateway.
- Cap nhat `run_all.ps1` de chay Django bang `--noreload`, giup moi service chi dung mot process on dinh va giam nguy co timeout/stale process khi chay local.
- `run_all.ps1` chi dung cac process `manage.py runserver` thuoc workspace hien tai, tranh dong nham cac Python process khac tren may.

### Cap nhat 2026-06-12 20:35 - Giao dien light template
- Da them giao dien web tai `gateway-service` route `/` tren port `8008`.
- Da them proxy API `/ui/api/*` trong gateway de UI goi cac service ma khong can cau hinh CORS rieng cho tung service.
- UI ho tro: service status, login demo, catalog/search, cart, checkout, create order, payment confirm, shipment delivered, AI behavior va customer metadata.
- Da tao `checklist.md` gom ha tang, backend services, giao dien, kiem thu va cac viec con lai neu muon hoan thien production.
- Da verify: `manage.py check` pass cho 8 service, `/` tra HTTP 200, `/ui/api/status`, `/ui/api/products`, `/ui/api/login` hoat dong, va `test_flow.py` pass 16 buoc end-to-end.

### Cap nhat 2026-06-12 20:55 - Docker Compose full stack
- Da them `Dockerfile` dung chung cho 8 Django service va `.dockerignore`.
- Da mo rong `docker-compose.yml` thanh full stack: PostgreSQL + user/product/cart/order/payment/shipping/ai/gateway service.
- Da forward port ra local: PostgreSQL `5435`, API services `8001-8007`, gateway/UI `8008`.
- Da chuyen DB config sang bien moi truong `DB_HOST`, `DB_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`; local mac dinh van dung `localhost:5435`.
- Da chuyen inter-service URL sang bien moi truong; trong Docker cac service goi nhau bang service name noi bo.
- Da them profile `tools` cho `seed-data` de co the seed data trong container khi can.
- Da verify: `docker compose config --quiet`, `docker compose up --build -d`, `docker compose ps`, gateway local `http://127.0.0.1:8008/` HTTP 200, `/ui/api/status` online 8 service, va `test_flow.py` pass 16 buoc khi backend chay trong Docker.

### Cap nhat 2026-06-12 21:05 - Ke hoach admin/staff/shipper
- Da tao `plan_roles_frontend_backend_db.md` de mo rong he thong co day du role: `customer`, `admin`, `staff`, `shipper`.
- Yeu cau da ghi ro: khong can JWT, dung `role`, `X-User-Id` va `X-User-Role` de phan quyen nhanh cho demo.
- Ke hoach da bao gom backend API, frontend dashboard theo role, database fields can them, workflow order/shipping va thu tu trien khai lan sau.
- Da cap nhat `checklist.md` voi cac muc pending: role `shipper`, admin APIs/UI, staff APIs/UI, shipper APIs/UI, role-based checks, migration fields va integration test `test_admin_staff_shipper_flow.py`.
- Trang thai hien tai: PENDING, chua implement code cho admin/staff/shipper; lan sau nen bat dau tu `user-service` them role `shipper`, admin user APIs va seed `staff1`/`shipper1`.

### Cap nhat 2026-06-12 21:25 - Da apply admin/staff/shipper
- Da them role `shipper`, profile fields `full_name`, `phone` vao `user-service`; `is_active` dung field co san cua Django user.
- Da them admin user APIs: list/create/update/disable user va role lookup.
- Da mo rong `order-service`: `assigned_staff_id`, `confirmed_at`, `processing_at`, `cancelled_reason`; workflow status co `confirmed`, `ready_to_ship`, `shipping`; them admin/staff APIs.
- Da mo rong `shipping-service`: `shipper_id`, `assigned_at`, `picked_up_at`, `delivery_note`; them admin/staff assign shipper va shipper shipment APIs.
- Da them admin/staff payment APIs trong `payment-service`.
- Da mo rong `gateway-service`: proxy `/ui/api/admin/*`, `/ui/api/staff/*`, `/ui/api/shipper/*`; them category/product admin proxy.
- Da mo rong UI light template voi panel Role Operations va quick login cho `customer1`, `admin1`, `staff1`, `shipper1`.
- Da cap nhat `seed_data.py` de clear cart/order/payment/shipping/ai va tao demo users `customer1`, `admin1`, `staff1`, `shipper1`.
- Da them `test_admin_staff_shipper_flow.py`.
- Da rebuild Docker, apply migrations, seed lai data. Verification pass: `test_flow.py`, `test_admin_staff_shipper_flow.py`, gateway `/` HTTP 200, `/ui/api/status` online 8 service.
- Trang thai hien tai: DONE FOR DEMO. Phan co the nang cap sau: UI form CRUD product/category day du hon, permission production-grade, test rieng tung service.
