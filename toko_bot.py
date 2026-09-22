#!/usr/bin/env python3
"""
Toko Tanaman & Pupuk — WhatsApp Bot Demo
Fitur: catalog, order, inventory, auto-reply, laporan
"""

import json, csv, os, time
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"
PRODUCTS_FILE = f"{DATA_DIR}/products.json"
ORDERS_FILE = f"{DATA_DIR}/orders.csv"
INVENTORY_FILE = f"{DATA_DIR}/inventory.csv"

class TokoBot:
    def __init__(self):
        self.products = self._load_products()
        self.orders = self._load_orders()
        self._ensure_inventory()
    
    def _load_products(self):
        with open(PRODUCTS_FILE, 'r') as f:
            return json.load(f)
    
    def _load_orders(self):
        if not os.path.exists(ORDERS_FILE):
            return []
        orders = []
        with open(ORDERS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                orders.append(row)
        return orders
    
    def _ensure_inventory(self):
        if not os.path.exists(INVENTORY_FILE):
            with open(INVENTORY_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["product_id", "stock", "last_updated"])
            for cat, items in self.products.items():
                for p in items:
                    self._update_inventory(p["id"], p["stock"])
    
    def _update_inventory(self, product_id, stock):
        inventory = {}
        if os.path.exists(INVENTORY_FILE):
            with open(INVENTORY_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    inventory[row["product_id"]] = row
        
        inventory[product_id] = {
            "product_id": product_id,
            "stock": stock,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(INVENTORY_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["product_id", "stock", "last_updated"])
            writer.writeheader()
            for v in inventory.values():
                writer.writerow(v)
    
    def get_catalog(self):
        """Return formatted catalog"""
        msg = "🌿 *TOKO TANAMAN & PUPUK*🌿\n\n"
        for cat, items in self.products.items():
            msg += f"📦 *{cat.upper()}*\n"
            for p in items:
                stock_status = "✅" if p["stock"] > 10 else "⚠️" if p["stock"] > 0 else "❌"
                msg += f"  {stock_status} *{p['name']}* — Rp {p['price']:,}\n"
                msg += f"     ID: {p['id']} | Stok: {p['stock']}\n"
            msg += "\n"
        msg += "💬 Ketik *order <id> <jumlah>* untuk beli\n"
        msg += "📋 Ketik *catalog* untuk lihat daftar\n"
        msg += "📊 Ketik *stok* untuk cek inventory"
        return msg
    
    def search_product(self, query):
        """Search product by name or ID"""
        results = []
        query = query.lower()
        for cat, items in self.products.items():
            for p in items:
                if query in p["name"].lower() or query in p["id"].lower():
                    results.append(p)
        return results
    
    def place_order(self, product_id, quantity, customer_name="Customer"):
        """Place an order"""
        # Find product
        product = None
        for cat, items in self.products.items():
            for p in items:
                if p["id"] == product_id:
                    product = p
                    break
            if product:
                break
        
        if not product:
            return None, "❌ Produk tidak ditemukan"
        
        if product["stock"] < quantity:
            return None, f"❌ Stok tidak cukup. Tersedia: {product['stock']}"
        
        # Calculate
        total = product["price"] * quantity
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Update stock
        product["stock"] -= quantity
        self._update_inventory(product_id, product["stock"])
        
        # Save order
        order = {
            "order_id": order_id,
            "customer": customer_name,
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "unit_price": product["price"],
            "total": total,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }
        self.orders.append(order)
        
        # Save to CSV
        with open(ORDERS_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=order.keys())
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(order)
        
        return order, f"✅ *Pesanan Berhasil!*\n\n" \
               f"📦 {product['name']} x{quantity}\n" \
               f"💰 Total: Rp {total:,}\n" \
               f"🆔 Order ID: {order_id}\n" \
               f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n" \
               f"Transfer ke rekening toko & kirim bukti ✅"
    
    def get_inventory(self):
        """Return inventory report"""
        msg = "📊 *INVENTORY REPORT*\n\n"
        total_items = 0
        total_value = 0
        
        for cat, items in self.products.items():
            msg += f"📦 *{cat.upper()}*\n"
            for p in items:
                stock_status = "✅" if p["stock"] > 10 else "⚠️" if p["stock"] > 0 else "❌"
                value = p["price"] * p["stock"]
                total_items += p["stock"]
                total_value += value
                msg += f"  {stock_status} {p['name']}: {p['stock']} (Rp {value:,})\n"
            msg += "\n"
        
        msg += f"\n📈 *Total:* {total_items} item\n"
        msg += f"💰 *Total Nilai Inventori:* Rp {total_value:,}"
        return msg
    
    def get_orders(self, status=None):
        """Return order list"""
        if not self.orders:
            return "📭 Belum ada pesanan"
        
        msg = "📋 *DAFTAR PESANAN*\n\n"
        for o in reversed(self.orders):
            if status and o["status"] != status:
                continue
            msg += f"🆔 {o['order_id']}\n"
            msg += f"📦 {o['product_name']} x{o['quantity']}\n"
            msg += f"💰 Rp {int(o['total']):,}\n"
            msg += f"📌 Status: {o['status']}\n"
            msg += f"⏰ {o['timestamp']}\n\n"
        return msg

# ==========================================
# D. Demo simulation
# ==========================================
print("\n[4] Menjalankan demo...\n")

bot = TokoBot()

# Demo 1: Show catalog
print("--- DEMO 1: Catalog ---")
print(bot.get_catalog())
print()

# Demo 2: Search product
print("--- DEMO 2: Search 'Kaktus' ---")
results = bot.search_product("Kaktus")
for r in results:
    print(f"  Found: {r['name']} - Rp {r['price']:,} (stok: {r['stock']})")
print()

# Demo 3: Place order
print("--- DEMO 3: Order T004 x3 ---")
order, msg = bot.place_order("T004", 3, "Budi")
print(msg)
print()

# Demo 4: Check inventory
print("--- DEMO 4: Inventory Report ---")
print(bot.get_inventory())
print()

# Demo 5: Show orders
print("--- DEMO 5: Orders ---")
print(bot.get_orders())
print()

# Demo 6: Low stock alert
print("--- DEMO 6: Low Stock Alert ---")
low_stock = []
for cat, items in bot.products.items():
    for p in items:
        if p["stock"] < 10:
            low_stock.append(p)
if low_stock:
    print("⚠️ Stok rendah:")
    for p in low_stock:
        print(f"  {p['name']}: {p['stock']} tersisa")
else:
    print("✅ Semua stok cukup")

print("\n" + "=" * 70)
print("DEMO SELESAI")
print("=" * 70)
