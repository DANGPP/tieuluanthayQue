import sys
import requests
import time

# Reconfigure output to support UTF-8 on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

USER_SVC = "http://127.0.0.1:8001/api"
PRODUCT_SVC = "http://127.0.0.1:8002/api"
CART_SVC = "http://127.0.0.1:8003/api"
ORDER_SVC = "http://127.0.0.1:8004/api"
PAYMENT_SVC = "http://127.0.0.1:8005/api"
SHIPPING_SVC = "http://127.0.0.1:8006/api"
AI_SVC = "http://127.0.0.1:8007/api"
GATEWAY_SVC = "http://127.0.0.1:8008/api"

def run_integration_test():
    print("==================================================")
    print("STARTING END-TO-END MICROSERVICES INTEGRATION TEST")
    print("==================================================")
    
    # 1. Login user customer1
    print("\n[Step 1] Logging in as customer1...")
    login_payload = {"username": "customer1", "password": "password123"}
    try:
        res = requests.post(f"{USER_SVC}/auth/login", json=login_payload, timeout=15)
        if res.status_code != 200:
            print("FAILED: Login failed.", res.json())
            return
        login_data = res.json()
        user_id = login_data['user']['id']
        username = login_data['user']['username']
        print(f"SUCCESS: Logged in! User ID: {user_id}, Username: {username}")
    except Exception as e:
        print("FAILED to connect to User Service:", str(e))
        return

    headers = {'X-User-Id': str(user_id)}

    # 2. Get Product Catalog
    print("\n[Step 2] Fetching Product Catalog from Product Service...")
    try:
        res = requests.get(f"{PRODUCT_SVC}/products", timeout=15)
        if res.status_code != 200:
            print("FAILED: Fetch products failed.", res.json())
            return
        products = res.json()
        print(f"SUCCESS: Found {len(products)} products in catalog:")
        for p in products:
            print(f"  - ID {p['id']}: {p['name']} ({p['price']} VND) - Stock: {p['stock']}")
        if not products:
            print("FAILED: Seeding did not create products.")
            return
        
        # Pick first product (the book)
        book_id = products[0]['id']
        book_price = float(products[0]['price'])
    except Exception as e:
        print("FAILED to connect to Product Service:", str(e))
        return

    # 3. Add item to cart
    print(f"\n[Step 3] Adding 2 units of product ID {book_id} to cart...")
    cart_payload = {"product_id": book_id, "quantity": 2}
    try:
        res = requests.post(f"{CART_SVC}/cart/items", json=cart_payload, headers=headers, timeout=15)
        if res.status_code != 201:
            print("FAILED: Add to cart failed.", res.json())
            return
        print("SUCCESS: Product added to cart.", res.json())
    except Exception as e:
        print("FAILED to connect to Cart Service:", str(e))
        return

    # 4. Preview cart checkout
    print("\n[Step 4] Requesting Checkout Preview...")
    try:
        res = requests.get(f"{CART_SVC}/cart/checkout-preview", headers=headers, timeout=15)
        if res.status_code != 200:
            print("FAILED: Checkout preview failed.", res.json())
            return
        preview_data = res.json()
        print(f"SUCCESS: Preview Data -> Total Price: {preview_data['total_price']} VND")
        for item in preview_data['items']:
            print(f"  - Item: {item['product_name']}, Qty: {item['quantity']}, Subtotal: {item['subtotal']} VND")
        total_price = preview_data['total_price']
    except Exception as e:
        print("FAILED to connect to Cart Service checkout-preview:", str(e))
        return

    # 5. Fetch default address
    print("\n[Step 5] Fetching default address from User Service...")
    try:
        res = requests.get(f"{USER_SVC}/users/me/addresses", headers=headers, timeout=15)
        if res.status_code != 200:
            print("FAILED: Fetch addresses failed.", res.json())
            return
        addresses = res.json()
        if not addresses:
            print("FAILED: User has no address.")
            return
        address_id = addresses[0]['id']
        print(f"SUCCESS: Address ID {address_id} found -> {addresses[0]['address_line']}")
    except Exception as e:
        print("FAILED to retrieve address:", str(e))
        return

    # 6. Create Order
    print(f"\n[Step 6] Creating Order with address ID {address_id}...")
    order_payload = {"address_id": address_id}
    try:
        res = requests.post(f"{ORDER_SVC}/orders", json=order_payload, headers=headers, timeout=15)
        if res.status_code != 201:
            print("FAILED: Create order failed.", res.json())
            return
        order_data = res.json()
        order_id = order_data['id']
        print(f"SUCCESS: Order created! ID: {order_id}, Status: {order_data['status']}, Total: {order_data['total_price']} VND")
    except Exception as e:
        print("FAILED to connect to Order Service:", str(e))
        return

    # 7. Check stock reduction
    print(f"\n[Step 7] Checking if product ID {book_id} stock was reduced...")
    try:
        res = requests.get(f"{PRODUCT_SVC}/products/{book_id}", timeout=15)
        if res.status_code == 200:
            new_stock = res.json()['stock']
            print(f"SUCCESS: Stock updated. New stock: {new_stock}")
        else:
            print("FAILED to check product stock.")
    except Exception as e:
        print("FAILED to connect to Product Service for stock check:", str(e))

    # 8. Create Payment Intent
    print(f"\n[Step 8] Creating Payment Intent for Order {order_id}...")
    pay_payload = {"order_id": order_id, "amount": total_price, "method": "card"}
    try:
        res = requests.post(f"{PAYMENT_SVC}/payments", json=pay_payload, timeout=15)
        if res.status_code != 201:
            print("FAILED: Payment creation failed.", res.json())
            return
        payment_data = res.json()
        payment_id = payment_data['id']
        print(f"SUCCESS: Payment Intent created! ID: {payment_id}, Status: {payment_data['status']}")
    except Exception as e:
        print("FAILED to connect to Payment Service:", str(e))
        return

    # 9. Confirm Payment (Webhook Callback Simulation)
    print(f"\n[Step 9] Simulating Webhook Callback to confirm Payment {payment_id}...")
    confirm_payload = {"transaction_id": f"TXN_{payment_id}_{int(time.time())}", "status": "success"}
    try:
        res = requests.post(f"{PAYMENT_SVC}/payments/{payment_id}/confirm", json=confirm_payload, headers=headers, timeout=15)
        if res.status_code != 200:
            print("FAILED: Payment confirmation failed.", res.json())
            return
        print(f"SUCCESS: Payment confirmed. Transaction ID: {res.json()['transaction_id']}, Payment Status: {res.json()['status']}")
    except Exception as e:
        print("FAILED to connect to Payment Service confirm:", str(e))
        return

    # Give downstream services a second to process in background
    time.sleep(1.5)

    # 10. Check Order Status update
    print(f"\n[Step 10] Checking Order {order_id} status in Order Service...")
    try:
        res = requests.get(f"{ORDER_SVC}/orders/{order_id}", headers=headers, timeout=15)
        if res.status_code == 200:
            print(f"SUCCESS: Current Order Status: {res.json()['status']}")
        else:
            print("FAILED: Get order status failed.", res.json())
    except Exception as e:
        print("FAILED to check order status:", str(e))

    # 11. Retrieve Shipment details
    print(f"\n[Step 11] Checking Shipment details for Order {order_id}...")
    try:
        res = requests.get(f"{SHIPPING_SVC}/shipments/order/{order_id}", timeout=15)
        if res.status_code == 200:
            shipment_data = res.json()
            shipment_id = shipment_data['id']
            print(f"SUCCESS: Shipment created! Tracking: {shipment_data['tracking_number']}, Status: {shipment_data['status']}")
        else:
            print("FAILED: Shipment not found.", res.json())
            return
    except Exception as e:
        print("FAILED to check shipment details:", str(e))
        return

    # 12. Update shipment to delivered
    print(f"\n[Step 12] Simulating driver updating shipment {shipment_id} status to 'delivered'...")
    try:
        res = requests.put(f"{SHIPPING_SVC}/shipments/{shipment_id}", json={"status": "delivered"}, timeout=15)
        if res.status_code == 200:
            print(f"SUCCESS: Shipment status updated. Status: {res.json()['status']}")
        else:
            print("FAILED to update shipment.", res.json())
            return
    except Exception as e:
        print("FAILED to update shipment details:", str(e))
        return

    # Give background process a split second
    time.sleep(1)

    # 13. Verify order status is completed
    print(f"\n[Step 13] Verifying Order {order_id} status is now 'completed'...")
    try:
        res = requests.get(f"{ORDER_SVC}/orders/{order_id}", headers=headers, timeout=15)
        if res.status_code == 200:
            print(f"SUCCESS: Order Status is now: {res.json()['status']}")
        else:
            print("FAILED to verify final order status.")
    except Exception as e:
        print("FAILED to check order status:", str(e))

    # 14. Log user behavior to AI Service
    print(f"\n[Step 14] Logging user purchase behavior to AI Service...")
    ai_payload = {"user_id": user_id, "product_id": book_id, "action_type": "purchase"}
    try:
        res = requests.post(f"{AI_SVC}/ai/behaviors", json=ai_payload, timeout=15)
        if res.status_code == 201:
            print("SUCCESS: User purchase behavior logged in AI Service.")
        else:
            print("FAILED to log AI behavior.", res.json())
    except Exception as e:
        print("FAILED to connect to AI Service:", str(e))

    # 15. Check AI logs
    print(f"\n[Step 15] Fetching logged behaviors from AI Service...")
    try:
        res = requests.get(f"{AI_SVC}/ai/behaviors?user_id={user_id}", timeout=15)
        if res.status_code == 200:
            behaviors = res.json()
            print(f"SUCCESS: Retrieved {len(behaviors)} logged behaviors from AI Service.")
            for b in behaviors:
                print(f"  - Action: {b['action_type']} on Product {b['product_id']} at {b['timestamp']}")
        else:
            print("FAILED to fetch AI behaviors.")
    except Exception as e:
        print("FAILED to query AI Service:", str(e))

    # 16. Get gateway customer metadata
    print(f"\n[Step 16] Fetching gateway customers metadata...")
    try:
        res = requests.get(f"{GATEWAY_SVC}/gateway/customers", timeout=15)
        if res.status_code == 200:
            customers = res.json()
            print(f"SUCCESS: Retrieved gateway customers metadata:")
            for c in customers:
                print(f"  - Customer: {c['full_name']} | Email: {c['email']} | Address: {c['address']}")
        else:
            print("FAILED to retrieve gateway customer metadata.")
    except Exception as e:
        print("FAILED to query Gateway Service:", str(e))

    print("\n==================================================")
    print("INTEGRATION TEST COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_integration_test()
