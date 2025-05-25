import frappe
import json
import requests

def sync_orders_from_store(store):
    """
    مزامنة الطلبات من متجر خارجي إلى ERPNext
    """
    if not store.enabled or not store.sync_orders:
        return

    headers = {
        "Authorization": f"Bearer {store.api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{store.base_url}/api/orders", headers=headers)

        if response.status_code != 200:
            frappe.log_error(f"فشل في جلب الطلبات من المتجر {store.name}", "Sync Orders Error")
            return

        orders = response.json()

        for order in orders:
            external_id = str(order.get("id"))
            if not external_id:
                continue

            exists = frappe.db.exists("External Order", {
                "store": store.name,
                "external_id": external_id
            })
            if exists:
                continue

            frappe.get_doc({
                "doctype": "External Order",
                "store": store.name,
                "external_id": external_id,
                "order_status": order.get("status"),
                "customer_name": order.get("customer", {}).get("name"),
                "total_amount": order.get("total"),
                "payload": json.dumps(order),
                "synced_to_erp": 0
            }).insert(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(f"خطأ أثناء مزامنة الطلبات: {str(e)}", "Sync Orders")


        
def convert_external_orders_to_sales_orders():
    """
    تحويل الطلبات الخارجية إلى Sales Orders في ERPNext
    """
    external_orders = frappe.get_all("External Order", filters={"synced_to_erp": 0}, fields=["name"])

    for eo in external_orders:
        order_doc = frappe.get_doc("External Order", eo.name)
        try:
            payload = json.loads(order_doc.payload)

            customer_name = payload.get("customer", {}).get("name") or order_doc.customer_name
            customer_email = payload.get("customer", {}).get("email")

            # التحقق من العميل أو إنشاؤه
            customer = get_or_create_customer(customer_name, customer_email)

            # بناء عناصر الطلب (مبسطة - عدّل حسب بنية الـ payload)
            items = []
            for item in payload.get("items", []):
                items.append({
                    "item_code": item.get("sku"),
                    "qty": item.get("quantity"),
                    "rate": item.get("price")
                })

            so = frappe.get_doc({
                "doctype": "Sales Order",
                "customer": customer.name,
                "items": items
            }).insert(ignore_permissions=True)

            # تحديث External Order
            order_doc.db_set("synced_to_erp", 1)
            order_doc.db_set("sales_order", so.name)

            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"فشل في تحويل External Order {eo.name} إلى Sales Order: {str(e)}", "Convert Orders")
