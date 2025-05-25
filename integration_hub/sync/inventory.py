import frappe
import json
import requests

def sync_inventory_from_store(store):
    """
    مزامنة بيانات المخزون من المتجر الخارجي إلى ERPNext
    """
    if not store.enabled or not store.sync_inventory:
        return

    headers = {
        "Authorization": f"Bearer {store.api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{store.base_url}/api/inventory", headers=headers)

        if response.status_code != 200:
            frappe.log_error(f"فشل في جلب بيانات المخزون من المتجر {store.name}", "Sync Inventory Error")
            return

        inventory_items = response.json()

        for item in inventory_items:
            external_sku = item.get("sku")
            if not external_sku:
                continue

            exists = frappe.db.exists("External Inventory", {
                "store": store.name,
                "external_sku": external_sku
            })
            if exists:
                continue

            frappe.get_doc({
                "doctype": "External Inventory",
                "store": store.name,
                "external_sku": external_sku,
                "quantity": item.get("quantity"),
                "warehouse": item.get("warehouse"),  # إذا كان موجودًا
                "payload": json.dumps(item),
                "synced_to_erp": 0
            }).insert(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(f"خطأ أثناء مزامنة المخزون: {str(e)}", "Sync Inventory")


def convert_external_inventory_to_stock_entries():
    """
    تحويل بيانات المخزون الخارجي إلى Stock Entry من نوع 'Material Receipt'
    """
    external_items = frappe.get_all("External Inventory", filters={"synced_to_erp": 0}, fields=["name"])

    for record in external_items:
        try:
            doc = frappe.get_doc("External Inventory", record.name)
            sku = doc.external_sku
            qty = doc.quantity or 0
            warehouse = doc.warehouse or "Stores - "  # غيّر إلى مستودعك الافتراضي

            if not sku or qty <= 0:
                continue

            item_exists = frappe.db.exists("Item", {"item_code": sku})
            if not item_exists:
                frappe.log_error(f"المنتج غير موجود: {sku}", "Inventory Sync")
                continue

            stock_entry = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Receipt",
                "items": [{
                    "item_code": sku,
                    "qty": qty,
                    "t_warehouse": warehouse
                }]
            }).insert(ignore_permissions=True)

            # تحديث سجل External Inventory
            doc.db_set("synced_to_erp", 1)
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"خطأ أثناء تحويل External Inventory {record.name} إلى Stock Entry: {str(e)}", "Inventory Conversion")
