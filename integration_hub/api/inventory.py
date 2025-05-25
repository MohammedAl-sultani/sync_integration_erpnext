import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_inventory(store_name, sku=None, name=None, warehouse_id=None, limit=20, offset=0):
    """
    إرجاع قائمة من المنتجات المخزنة مع دعم التصفية والترقيم.
    """
    filters = {"store": store_name}
    if sku:
        filters["external_sku"] = ["like", f"%{sku}%"]
    if name:
        filters["item_name"] = ["like", f"%{name}%"]
    if warehouse_id:
        filters["warehouse"] = warehouse_id

    records = frappe.get_all(
        "External Inventory",
        filters=filters,
        fields=["external_sku as sku", "item_name as name", "warehouse", "quantity"],
        limit_page_length=int(limit),
        limit_start=int(offset),
        order_by="modified desc"
    )

    return records


@frappe.whitelist(allow_guest=True)
def get_inventory_total(store_name, sku=None, name=None, warehouse_id=None):
    """
    إرجاع العدد الإجمالي للمنتجات المطابقة للفلاتر.
    """
    filters = {"store": store_name}
    if sku:
        filters["external_sku"] = ["like", f"%{sku}%"]
    if name:
        filters["item_name"] = ["like", f"%{name}%"]
    if warehouse_id:
        filters["warehouse"] = warehouse_id

    total = frappe.db.count("External Inventory", filters)
    return {"total": total}
