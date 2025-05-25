import frappe
import json
import requests

def sync_customers_from_store(store):
    """
    مزامنة العملاء من متجر خارجي إلى ERPNext
    """
    if not store.enabled or not store.sync_customers:
        return

    # إعداد التوثيق
    headers = {
        "Authorization": f"Bearer {store.api_key}",
        "Content-Type": "application/json"
    }

    try:
        # إرسال طلب إلى API المتجر الخارجي (مثال تجريبي)
        response = requests.get(f"{store.base_url}/api/customers", headers=headers)

        if response.status_code != 200:
            frappe.log_error(f"فشل في جلب العملاء من المتجر {store.name}", "Sync Customers Error")
            return

        customers = response.json()

        for customer in customers:
            external_id = str(customer.get("id"))
            if not external_id:
                continue

            # تحقق من وجود العميل مسبقًا
            exists = frappe.db.exists("External Customer", {
                "store": store.name,
                "external_id": external_id
            })
            if exists:
                continue

            # إنشاء سجل جديد في External Customer
            frappe.get_doc({
                "doctype": "External Customer",
                "store": store.name,
                "external_id": external_id,
                "customer_name": customer.get("name"),
                "email": customer.get("email"),
                "phone": customer.get("phone"),
                "payload": json.dumps(customer),
                "synced_to_erp": 0
            }).insert(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(f"خطأ أثناء مزامنة العملاء: {str(e)}", "Sync Customers")
def get_or_create_customer(name, email=None):
    existing = frappe.db.get_value("Customer", {"customer_name": name})
    if existing:
        return frappe.get_doc("Customer", existing)

    doc = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": name,
        "customer_type": "Individual",
        "customer_group": "Individual",
        "territory": "All Territories",
        "email_id": email
    }).insert(ignore_permissions=True)

    return doc
