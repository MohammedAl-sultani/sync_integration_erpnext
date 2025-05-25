import json
import frappe
from frappe.model.document import Document

# استيراد وظائف المزامنة
from integration_hub.sync.customers import sync_customers_from_store
from integration_hub.sync.products import sync_products_from_store, convert_external_products_to_items
from integration_hub.sync.orders import sync_orders_from_store, convert_external_orders_to_sales_orders
from integration_hub.sync.inventory import sync_inventory_from_store, convert_external_inventory_to_stock_entries


class IntegrationStore(Document):
    def sync_now(self):
        """
        تنفيذ المزامنة حسب الإعدادات المحددة لكل متجر.
        تشمل المزامنة العملاء، المنتجات، الطلبات، والمخزون.
        وتقوم بتحويل السجلات إلى مستندات ERPNext الفعلية مباشرة بعد المزامنة.
        """

        # مزامنة العملاء
        if self.sync_customers:
            sync_customers_from_store(self)

        # مزامنة المنتجات وتحويلها إلى Items
        if self.sync_products:
            sync_products_from_store(self)
            convert_external_products_to_items()

        # مزامنة الطلبات وتحويلها إلى Sales Orders
        if self.sync_orders:
            sync_orders_from_store(self)
            convert_external_orders_to_sales_orders()

        # مزامنة بيانات المخزون وتحويلها إلى Stock Entries
        if self.sync_inventory:
            sync_inventory_from_store(self)
            convert_external_inventory_to_stock_entries()

        frappe.msgprint("✅ تم تنفيذ المزامنة والتحويل بنجاح حسب الإعدادات المحددة.")


@frappe.whitelist()
def run_sync_now(doc):
    """
    دالة واجهة (API) لاستدعاء المزامنة من الواجهة.
    تتلقى المستند كـ JSON وتقوم باستدعاء sync_now().
    """
    doc = frappe.get_doc(json.loads(doc))
    if hasattr(doc, "sync_now"):
        doc.sync_now()
