import frappe
import json
import requests

def sync_products_from_store(store):
    """
    مزامنة المنتجات من متجر خارجي إلى ERPNext
    """
    if not store.enabled or not store.sync_products:
        return

    headers = {
        "Authorization": f"Bearer {store.api_key}",
        "Content-Type": "application/json"
    }

    try:
        # جلب قائمة المنتجات من API المتجر
        response = requests.get(f"{store.base_url}/api/products", headers=headers)

        if response.status_code != 200:
            frappe.log_error(f"فشل في جلب المنتجات من المتجر {store.name}", "Sync Products Error")
            return

        products = response.json()

        for product in products:
            external_id = str(product.get("id"))
            if not external_id:
                continue

            exists = frappe.db.exists("External Product", {
                "store": store.name,
                "external_id": external_id
            })
            if exists:
                continue

            frappe.get_doc({
                "doctype": "External Product",
                "store": store.name,
                "external_id": external_id,
                "product_name": product.get("name"),
                "sku": product.get("sku"),
                "payload": json.dumps(product),
                "synced_to_erp": 0
            }).insert(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(f"خطأ أثناء مزامنة المنتجات: {str(e)}", "Sync Products")
        
def convert_external_products_to_items():
    """
    تحويل المنتجات الخارجية إلى منتجات حقيقية في ERPNext (Item)
    """
    products = frappe.get_all("External Product", filters={"synced_to_erp": 0}, fields=["name"])

    for p in products:
        try:
            product_doc = frappe.get_doc("External Product", p.name)
            data = json.loads(product_doc.payload)

            sku = product_doc.sku or data.get("sku")
            name = product_doc.product_name or data.get("name")

            # التحقق من وجود المنتج مسبقًا
            existing = frappe.db.exists("Item", {"item_code": sku})
            if existing:
                product_doc.db_set("item_code", existing)
                product_doc.db_set("synced_to_erp", 1)
                continue

            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": sku,
                "item_name": name,
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
                "is_stock_item": 1,
                "description": data.get("description") or name
            }).insert(ignore_permissions=True)

            product_doc.db_set("item_code", item.name)
            product_doc.db_set("synced_to_erp", 1)
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"خطأ أثناء تحويل External Product {p.name} إلى Item: {str(e)}", "Convert Products")
