import sys
import time
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

GATEWAY = "http://127.0.0.1:8008"


def call(method, path, **kwargs):
    response = requests.request(method, f"{GATEWAY}{path}", timeout=20, **kwargs)
    try:
        data = response.json()
    except ValueError:
        data = {"raw": response.text}
    if response.status_code >= 400:
        raise RuntimeError(f"{method} {path} failed: {response.status_code} {data}")
    return data


def login(username):
    data = call(
        "POST",
        "/ui/api/login",
        json={"username": username, "password": "password123"},
    )
    user = data["user"]
    print(f"LOGIN {username}: id={user['id']} role={user['role']}")
    return user


def actor(user):
    return f"user_id={user['id']}&role={user['role']}"


def main():
    print("==================================================")
    print("ADMIN / STAFF / SHIPPER ROLE FLOW TEST")
    print("==================================================")

    admin = login("admin1")
    staff = login("staff1")
    shipper = login("shipper1")
    customer = login("customer1")

    users = call("GET", f"/ui/api/admin/users?{actor(admin)}")
    roles = {user["username"]: user["role"] for user in users}
    assert roles["staff1"] == "staff"
    assert roles["shipper1"] == "shipper"
    print("ADMIN: user list includes staff1 and shipper1.")

    products = call("GET", "/ui/api/products")
    if not products:
        raise RuntimeError("No products available.")
    product = products[0]
    print(f"CUSTOMER: selected product #{product['id']} - {product['name']}")

    call(
        "POST",
        "/ui/api/cart/items",
        json={"user_id": customer["id"], "role": customer["role"], "product_id": product["id"], "quantity": 1},
    )
    preview = call("GET", f"/ui/api/cart/checkout-preview?{actor(customer)}")
    print(f"CUSTOMER: checkout total = {preview['total_price']}")

    addresses = call("GET", f"/ui/api/addresses?{actor(customer)}")
    if not addresses:
        raise RuntimeError("Customer has no address.")
    order = call(
        "POST",
        "/ui/api/orders",
        json={"user_id": customer["id"], "role": customer["role"], "address_id": addresses[0]["id"]},
    )
    print(f"CUSTOMER: created order #{order['id']} status={order['status']}")

    payment = call(
        "POST",
        "/ui/api/payments",
        json={"order_id": order["id"], "amount": order["total_price"], "method": "card"},
    )
    payment = call(
        "POST",
        f"/ui/api/payments/{payment['id']}/confirm",
        json={
            "user_id": customer["id"],
            "role": customer["role"],
            "transaction_id": f"ROLE_TXN_{payment['id']}_{int(time.time())}",
            "status": "success",
        },
    )
    print(f"PAYMENT: payment #{payment['id']} status={payment['status']}")

    order = call("GET", f"/ui/api/admin/orders/{order['id']}?{actor(admin)}")
    print(f"ADMIN: order #{order['id']} after payment status={order['status']}")

    order = call(
        "PUT",
        f"/ui/api/admin/orders/{order['id']}/assign-staff",
        json={"user_id": admin["id"], "role": admin["role"], "staff_id": staff["id"]},
    )
    assert order["assigned_staff_id"] == staff["id"]
    print(f"ADMIN: assigned staff #{staff['id']} to order #{order['id']}")

    order = call(
        "PUT",
        f"/ui/api/staff/orders/{order['id']}/confirm",
        json={"user_id": staff["id"], "role": staff["role"]},
    )
    print(f"STAFF: confirmed order #{order['id']} status={order['status']}")

    order = call(
        "PUT",
        f"/ui/api/staff/orders/{order['id']}/ready-to-ship",
        json={"user_id": staff["id"], "role": staff["role"]},
    )
    print(f"STAFF: order #{order['id']} status={order['status']}")

    shipment = call("GET", f"/ui/api/shipments/order/{order['id']}")
    shipment = call(
        "PUT",
        f"/ui/api/admin/shipments/{shipment['id']}/assign-shipper",
        json={"user_id": admin["id"], "role": admin["role"], "shipper_id": shipper["id"]},
    )
    assert shipment["shipper_id"] == shipper["id"]
    print(f"ADMIN: assigned shipper #{shipper['id']} to shipment #{shipment['id']}")

    assigned = call("GET", f"/ui/api/shipper/shipments?{actor(shipper)}")
    assert any(item["id"] == shipment["id"] for item in assigned)
    print(f"SHIPPER: sees assigned shipment #{shipment['id']}")

    shipment = call(
        "PUT",
        f"/ui/api/shipper/shipments/{shipment['id']}/status",
        json={"user_id": shipper["id"], "role": shipper["role"], "status": "delivered"},
    )
    print(f"SHIPPER: shipment #{shipment['id']} status={shipment['status']}")

    final_order = call("GET", f"/ui/api/admin/orders/{order['id']}?{actor(admin)}")
    assert final_order["status"] == "completed"
    print(f"SUCCESS: final order #{final_order['id']} status={final_order['status']}")

    print("==================================================")
    print("ROLE FLOW TEST COMPLETED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    main()
