# Ke Hoach Mo Rong: Admin, Staff, Shipper Va Customer UI

Cap nhat: 2026-06-12 21:05

## 1. Muc tieu

Mo rong he thong e-commerce hien tai tu customer demo flow thanh he thong co day du vai tro van hanh:

- `customer`: dang ky, dang nhap, xem san pham, gio hang, dat hang, theo doi don.
- `admin`: quan tri toan he thong, quan ly user/staff/shipper, san pham, don hang, thanh toan, van chuyen.
- `staff`: xu ly don hang, cap nhat trang thai xu ly, kiem tra payment/shipping.
- `shipper`: nhan don giao, cap nhat trang thai giao hang.

Khong dung JWT trong giai do nay. Phan quyen lam nhanh bang `role` va header/session demo:

- Backend tiep tuc chap nhan `X-User-Id`.
- Gateway UI luu user dang nhap trong browser state/localStorage.
- Moi API noi bo can check role bang cach goi `user-service` hoac doc role tu header do gateway proxy gan vao.

## 2. Dieu Chinh Kien Truc

Giu 8 microservices hien tai, khong tao service moi trong giai do nhanh:

- `user-service`: mo rong user role va profile.
- `product-service`: them API quan tri san pham cho admin/staff.
- `order-service`: them workflow xu ly don cho staff/admin.
- `payment-service`: them API tra cuu/quan ly payment cho admin/staff.
- `shipping-service`: them shipper assignment va shipper workflow.
- `gateway-service`: them UI theo role va proxy role-based.

## 3. Backend Can Bo Sung

### 3.1 User Service

Model hien co:

- `User`
- `Address`

Can bo sung:

- Them role `shipper` vao `ROLE_CHOICES`.
- Them cac field profile tuy chon cho van hanh:
  - `phone`
  - `full_name`
  - `is_active`

API can bo sung:

- `GET /api/users`: admin xem danh sach user.
- `POST /api/users`: admin tao user/staff/shipper.
- `PUT /api/users/{id}`: admin cap nhat thong tin/role/trang thai.
- `DELETE /api/users/{id}`: admin vo hieu hoa user, uu tien soft disable bang `is_active = False`.
- `GET /api/users?role=staff|shipper|customer`: loc user theo role.
- `GET /api/users/{id}/role`: service noi bo kiem tra role nhanh.

Quy tac phan quyen:

- `admin`: duoc CRUD user va doi role.
- `staff`: chi duoc xem user lien quan order neu can.
- `shipper`: chi duoc xem profile cua minh.
- `customer`: chi duoc xem/sua `me`.

### 3.2 Product Service

API hien co da co CRUD san pham. Can them convention phan quyen:

- `admin`: CRUD category va product.
- `staff`: xem va cap nhat stock.
- `customer`: chi xem/list/search.

API can bo sung hoac chuan hoa:

- `GET /api/admin/products`: admin/staff list san pham kem stock.
- `PATCH /api/admin/products/{id}/stock`: staff/admin cap nhat ton kho.
- `GET /api/admin/categories`: admin quan ly category.

### 3.3 Order Service

Model hien co:

- `Order`
- `OrderItem`

Can bo sung field:

- `assigned_staff_id` nullable.
- `confirmed_at` nullable.
- `processing_at` nullable.
- `cancelled_reason` nullable.

Workflow de xuat:

- `pending`: customer vua dat.
- `confirmed`: staff/admin xac nhan don.
- `processing`: dang dong goi/xu ly.
- `ready_to_ship`: san sang ban giao shipper.
- `shipping`: da gan shipper/dang giao.
- `completed`: da giao thanh cong.
- `cancelled`: da huy.

API can bo sung:

- `GET /api/admin/orders`: admin/staff xem tat ca don, loc theo status/user.
- `GET /api/admin/orders/{id}`: admin/staff xem chi tiet.
- `PUT /api/admin/orders/{id}/status`: admin/staff cap nhat status hop le.
- `PUT /api/admin/orders/{id}/assign-staff`: admin gan staff xu ly.
- `GET /api/staff/orders`: staff xem don duoc gan hoac don chua gan.
- `PUT /api/staff/orders/{id}/confirm`: staff xac nhan don.
- `PUT /api/staff/orders/{id}/ready-to-ship`: staff chuyen sang san sang giao.

Quy tac:

- Customer chi xem don cua minh.
- Staff chi thao tac don duoc gan hoac don chua gan theo policy demo.
- Admin thao tac tat ca.

### 3.4 Payment Service

Model hien co:

- `Payment`

Can bo sung API:

- `GET /api/admin/payments`: admin/staff xem danh sach payment.
- `GET /api/admin/payments/{id}`: xem chi tiet payment.
- `PUT /api/admin/payments/{id}/status`: admin/staff cap nhat/mocking trang thai payment khi demo.

Quy tac:

- Admin xem tat ca.
- Staff xem payment cua order dang xu ly.
- Customer chi xem payment cua order minh neu can.

### 3.5 Shipping Service

Model hien co:

- `Shipment`

Can bo sung field:

- `shipper_id` nullable, logical reference sang `user-service`.
- `assigned_at` nullable.
- `picked_up_at` nullable.
- `delivery_note` nullable.

Workflow de xuat:

- `pending`: shipment moi tao.
- `assigned`: da gan shipper.
- `picked_up`: shipper da lay hang.
- `in_transit`: dang giao.
- `out_for_delivery`: sap giao.
- `delivered`: giao thanh cong.
- `failed`: giao that bai.

API can bo sung:

- `GET /api/admin/shipments`: admin/staff xem tat ca shipment.
- `PUT /api/admin/shipments/{id}/assign-shipper`: admin/staff gan shipper.
- `GET /api/shipper/shipments`: shipper xem cac shipment cua minh.
- `PUT /api/shipper/shipments/{id}/status`: shipper cap nhat `picked_up`, `in_transit`, `out_for_delivery`, `delivered`, `failed`.
- `PUT /api/shipper/shipments/{id}/note`: shipper ghi chu giao hang.

Quy tac:

- Shipper chi update shipment duoc gan cho minh.
- Khi shipment `delivered`, shipping-service goi order-service cap nhat order `completed`.
- Khi shipment `failed`, order co the chuyen ve `shipping_failed` hoac giu `shipping` kem note, tuy demo.

### 3.6 Gateway Service

Can bo sung role-based proxy:

- Sau login, gateway/UI biet `role`.
- UI route van la `/`, nhung hien tab theo role.
- Gateway proxy gan header:
  - `X-User-Id`
  - `X-User-Role`

Proxy API can them:

- `/ui/api/admin/users`
- `/ui/api/admin/products`
- `/ui/api/admin/orders`
- `/ui/api/admin/payments`
- `/ui/api/admin/shipments`
- `/ui/api/staff/orders`
- `/ui/api/shipper/shipments`

## 4. Database Can Bo Sung

### 4.1 user_db

Bang `users`:

- Them role choice `shipper`.
- Them field neu lam profile nang cap:
  - `full_name VARCHAR(255) NULL`
  - `phone VARCHAR(50) NULL`
  - `is_active BOOLEAN DEFAULT TRUE`

Bang `addresses` giu nguyen.

### 4.2 order_db

Bang `orders`:

- `assigned_staff_id INT NULL`
- `confirmed_at TIMESTAMP NULL`
- `processing_at TIMESTAMP NULL`
- `cancelled_reason TEXT NULL`
- Mo rong `status`.

Bang `order_items` giu nguyen.

### 4.3 shipping_db

Bang `shipments`:

- `shipper_id INT NULL`
- `assigned_at TIMESTAMP NULL`
- `picked_up_at TIMESTAMP NULL`
- `delivery_note TEXT NULL`
- Mo rong `status` neu can.

### 4.4 gateway_db

Co the giu `Customer` nhu metadata demo.

Neu can luu UI/session demo:

- Khong bat buoc.
- Uu tien dung browser localStorage va API login.

## 5. Frontend Can Bo Sung

Frontend hien tai: light template trong gateway-service.

Can mo rong thanh dashboard co tab theo role:

### 5.1 Customer View

- Dang ky/dang nhap.
- Catalog/search.
- Cart.
- Checkout/order.
- Theo doi don hang va shipment.

### 5.2 Admin View

- Dashboard tong quan:
  - tong user
  - tong order
  - revenue demo
  - pending shipments
- Quan ly users:
  - tao admin/staff/customer/shipper
  - sua role
  - khoa/mo user
- Quan ly products/categories:
  - tao/sua/xoa san pham
  - cap nhat stock
- Quan ly orders:
  - xem tat ca don
  - gan staff
  - cap nhat status
- Quan ly payments:
  - xem payment status
- Quan ly shipments:
  - gan shipper
  - xem trang thai giao hang.

### 5.3 Staff View

- Danh sach order can xu ly.
- Xem chi tiet order.
- Xac nhan order.
- Chuyen order sang `processing` va `ready_to_ship`.
- Xem payment/shipping lien quan.

### 5.4 Shipper View

- Danh sach shipment duoc gan.
- Xem dia chi/tracking.
- Cap nhat trang thai giao hang.
- Ghi chu giao hang.

## 6. Thu Tu Trien Khai De Lần Sau Lam Tiep

1. User Service:
   - them role `shipper`
   - them admin user APIs
   - seed them `staff1` va `shipper1`

2. Gateway:
   - sau login luu role
   - them tab UI role-based
   - them proxy admin/staff/shipper APIs

3. Order Service:
   - mo rong status workflow
   - them assigned_staff_id
   - them admin/staff APIs

4. Shipping Service:
   - them shipper_id va delivery_note
   - them assign shipper API
   - them shipper APIs

5. Payment/Product:
   - them admin/staff list/update APIs neu UI can

6. Test:
   - viet `test_admin_staff_shipper_flow.py`
   - flow mong muon:
     - admin login
     - admin tao staff/shipper
     - customer tao order
     - staff confirm va ready_to_ship
     - admin/staff gan shipper
     - shipper update delivered
     - order thanh completed

## 7. Trang Thai

Trang thai hien tai: IMPLEMENTED FOR DEMO.

Da co:

- Customer flow.
- Role `admin`, `staff`, `customer` trong user model.
- Role `shipper` trong user model.
- Admin user APIs.
- Admin/staff order APIs.
- Admin/staff payment APIs.
- Admin/staff shipping assignment APIs.
- Shipper shipment APIs.
- Gateway proxy routes cho admin/staff/shipper.
- Gateway light UI co panel role operations.
- Seed data `customer1`, `admin1`, `staff1`, `shipper1`.
- Integration test `test_admin_staff_shipper_flow.py`.
- Docker Compose full stack.
- Gateway light UI.

Chua co / co the nang cap sau:

- UI admin tao/sua product chua lam thanh form day du, hien co proxy API product/category va dashboard van hanh co ban.
- Permission demo dang dua vao `X-User-Role`, chua phai security production.
- Chua tach frontend thanh app rieng; hien van la Django template trong gateway.
