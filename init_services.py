import os
import subprocess
import shutil

SERVICES = {
    'user-service': {'port': 8001, 'db': 'user_db', 'app': 'user_app'},
    'product-service': {'port': 8002, 'db': 'product_db', 'app': 'product_app'},
    'cart-service': {'port': 8003, 'db': 'cart_db', 'app': 'cart_app'},
    'order-service': {'port': 8004, 'db': 'order_db', 'app': 'order_app'},
    'payment-service': {'port': 8005, 'db': 'payment_db', 'app': 'payment_app'},
    'shipping-service': {'port': 8006, 'db': 'shipping_db', 'app': 'shipping_app'},
    'ai-service': {'port': 8007, 'db': 'ai_db', 'app': 'ai_app'},
    'gateway-service': {'port': 8008, 'db': 'gateway_db', 'app': 'gateway_app'},
}

workspace = r"d:\2026\thayque\tieuluan"
python_exe = os.path.join(workspace, ".venv", "Scripts", "python.exe")

os.makedirs(os.path.join(workspace, "services"), exist_ok=True)

for svc_name, info in SERVICES.items():
    svc_dir = os.path.join(workspace, "services", svc_name)
    if os.path.exists(svc_dir):
        print(f"Service {svc_name} already exists. Skipping initialization.")
        continue

    os.makedirs(svc_dir)
    print(f"Initializing {svc_name}...")

    # Run django-admin startproject config .
    subprocess.run([python_exe, "-m", "django", "startproject", "config", "."], cwd=svc_dir, check=True)

    # Run manage.py startapp <app_name>
    subprocess.run([python_exe, "manage.py", "startapp", info['app']], cwd=svc_dir, check=True)

    # Configure settings.py
    settings_path = os.path.join(svc_dir, "config", "settings.py")
    with open(settings_path, "r", encoding="utf-8") as f:
        settings_content = f.read()

    # 1. Update ALLOWED_HOSTS
    settings_content = settings_content.replace("ALLOWED_HOSTS = []", "ALLOWED_HOSTS = ['*']")

    # 2. Add 'rest_framework' and app to INSTALLED_APPS
    installed_apps_old = "INSTALLED_APPS = [\n"
    installed_apps_new = f"INSTALLED_APPS = [\n    'rest_framework',\n    '{info['app']}',\n"
    settings_content = settings_content.replace(installed_apps_old, installed_apps_new)

    # 3. Configure PostgreSQL Database
    old_databases = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""

    new_databases = f"""DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '{info['db']}',
        'USER': 'postgres',
        'PASSWORD': 'postgres_password',
        'HOST': 'localhost',
        'PORT': '5435',
    }}
}}"""
    settings_content = settings_content.replace(old_databases, new_databases)

    # 4. Set APPEND_SLASH = False to allow trailing slash-less REST URLs
    settings_content += "\nAPPEND_SLASH = False\n"

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(settings_content)

    print(f"Service {svc_name} configured successfully.")

print("All services initialized!")
