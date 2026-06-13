# Checklist Du An Microservices E-Commerce

Cap nhat: 2026-06-12 21:25

## Ha tang
- [x] Docker PostgreSQL chay tren port host `5435`.
- [x] Tao 8 database rieng: `user_db`, `product_db`, `cart_db`, `order_db`, `payment_db`, `shipping_db`, `ai_db`, `gateway_db`.
- [x] Moi service co Django project rieng trong `services/`.
- [x] `run_all.ps1` khoi dong 8 service port `8001` den `8008`.
- [x] `run_all.ps1` chay Django voi `--noreload` de giam process thua.
- [x] `logs/` ghi log rieng cho tung service.
- [x] Them Dockerfile dung chung cho 8 Django service.
- [x] Them `.dockerignore` de loai `.venv`, logs va cache khoi build context.
- [x] `docker-compose.yml` chay PostgreSQL + 8 Django service.
- [x] Docker Compose forward port local `8001-8008`, trong do gateway/UI la `8008`.
- [x] Docker Compose forward PostgreSQL local `5435`.
- [x] Cac service trong Docker goi nhau bang service name noi bo: `user-service`, `product-service`, `cart-service`, `order-service`, `payment-service`, `shipping-service`, `ai-service`, `gateway-service`.
- [x] Cac service doc DB host/port va inter-service URL tu bien moi truong.

## Backend Services
- [x] `user-service`: dang ky, dang nhap local, user profile, address API.
- [x] `product-service`: category API, product CRUD, 10 product subtype bang multi-table inheritance.
- [x] `cart-service`: cart API, add/update/delete item, checkout preview, kiem tra stock qua product-service.
- [x] `order-service`: tao order tu cart, snapshot gia, snapshot dia chi, tru stock, xem/huy order.
- [x] `payment-service`: tao payment, confirm payment, cap nhat order, tao shipment.
- [x] `shipping-service`: tao shipment, cap nhat delivery, cap nhat order thanh `completed`.
- [x] `ai-service`: ghi va doc `UserBehavior`.
- [x] `gateway-service`: customer metadata API.

## Giao Dien Light Template
- [x] Them route `/` tren `gateway-service`.
- [x] Them template `gateway_app/templates/gateway_app/index.html`.
- [x] Them proxy API `/ui/api/*` de browser chi goi gateway, tranh loi CORS.
- [x] Hien thi trang thai 8 service.
- [x] Dang nhap demo voi `customer1/password123`.
- [x] Hien thi danh sach san pham va tim kiem.
- [x] Them san pham vao gio hang.
- [x] Xem, tang/giam so luong va xoa gio hang.
- [x] Lay dia chi giao hang.
- [x] Tao order.
- [x] Tao payment va confirm payment.
- [x] Xem shipment va danh dau `delivered`.
- [x] Hien thi AI behavior va customer metadata.

## Ke Hoach Mo Rong Admin/Staff/Shipper
- [x] Lap ke hoach mo rong trong `plan_roles_frontend_backend_db.md`.
- [x] Them role `shipper` vao `user-service`.
- [x] Them field profile van hanh cho user: `full_name`, `phone`, `is_active`.
- [x] Them API admin quan ly users trong `user-service`.
- [x] Them seed data cho `staff1` va `shipper1`.
- [x] Them role-based check bang `role`/`X-User-Role`, khong dung JWT.
- [x] Them admin product/category APIs hoac proxy UI cho CRUD san pham.
- [x] Them admin/staff order APIs: list all, assign staff, update status.
- [x] Mo rong order status workflow: `pending`, `confirmed`, `processing`, `ready_to_ship`, `shipping`, `completed`, `cancelled`.
- [x] Them `assigned_staff_id`, `confirmed_at`, `processing_at`, `cancelled_reason` vao `Order`.
- [x] Them admin/staff payment APIs.
- [x] Them `shipper_id`, `assigned_at`, `picked_up_at`, `delivery_note` vao `Shipment`.
- [x] Them admin/staff assign shipper API.
- [x] Them shipper shipment APIs: list assigned, update status, update note.
- [x] Mo rong Gateway UI thanh dashboard theo role: customer/admin/staff/shipper.
- [x] Them Gateway proxy routes cho `/ui/api/admin/*`, `/ui/api/staff/*`, `/ui/api/shipper/*`.
- [x] Them integration test `test_admin_staff_shipper_flow.py`.

## Kiem Thu
- [x] `manage.py check` pass cho 8 service.
- [x] Gateway UI route `/` tra HTTP 200.
- [x] Gateway proxy status `/ui/api/status` tra online cho 8 service.
- [x] Gateway proxy products `/ui/api/products` tra danh sach product.
- [x] Gateway proxy login `/ui/api/login` dang nhap thanh cong.
- [x] `test_flow.py` pass 16 buoc end-to-end sau khi them UI.
- [x] `docker compose config --quiet` hop le.
- [x] `docker compose up --build -d` build va start thanh cong.
- [x] `docker compose ps` hien PostgreSQL healthy va 8 service up.
- [x] Docker gateway local `http://127.0.0.1:8008/` tra HTTP 200.
- [x] Docker gateway `/ui/api/status` tra online cho 8 service.
- [x] `test_flow.py` pass 16 buoc end-to-end khi backend chay trong Docker.
- [x] Migration moi apply thanh cong trong Docker cho `user_app`, `order_app`, `shipping_app`.
- [x] Seed data tao `customer1`, `admin1`, `staff1`, `shipper1`.
- [x] Seed data clear cart/order/payment/shipping/ai de test sach hon.
- [x] `test_admin_staff_shipper_flow.py` pass end-to-end qua Gateway trong Docker.

## Con Lai Neu Muon Hoan Thien Hon
- [ ] Them test tu dong rieng cho tung service.
- [ ] Lam dep/lam sach encoding trong `plan.md` va mot phan `history.md`.
- [ ] Mo rong AI: ChromaDB, Neo4j/RAG, training RNN/LSTM/BiLSTM.
- [ ] Them CORS/security config dung production.
