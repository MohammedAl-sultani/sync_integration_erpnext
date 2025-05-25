# 🔗 Integration Hub for ERPNext

نظام تكاملي شامل يربط بين ERPNext والمنصات الخارجية مثل **OpenCart، WooCommerce، Shopify، Magento** وغيرها.

يوفر مزامنة **ثنائية الاتجاه** لجميع البيانات المهمة:

- ✅ المنتجات (Products)
- ✅ العملاء (Customers)
- ✅ الطلبات (Orders)
- ✅ المخزون (Inventory)

---

## 🚀 مزايا النظام

- مزامنة تلقائية وجدولة
- مزامنة من المتجر إلى ERPNext والعكس
- قابلية التوسعة لدعم أي منصة خارجية
- واجهات API REST مرنة مع توثيق Swagger

---

## 🧩 الموديلات الأساسية

- `Integration Store`: إعدادات الربط
- `External Product`, `External Customer`, `External Order`, `External Inventory`: نماذج وسيطة
- تحويل تلقائي إلى `Item`, `Customer`, `Sales Order`, `Stock Entry`

---

## 📘 التوثيق التفاعلي (Swagger UI)

واجهة API مرئية واختبار مباشر عبر المتصفح:

📎 افتح الرابط:

http://localhost:8000/assets/integration_hub/swagger/index.html


### ✅ أهم المسارات

| العملية                         | نوع الطلب | الرابط |
|----------------------------------|-----------|--------|
| 🔄 مزامنة المنتجات               | `POST`    | `/method/integration_hub.api.sync_products` |
| 📤 إرسال المنتجات للمتجر        | `POST`    | `/method/integration_hub.api.send_products` |
| 👥 مزامنة العملاء               | `POST`    | `/method/integration_hub.api.sync_customers` |
| 📤 إرسال العملاء للمتجر         | `POST`    | `/method/integration_hub.api.send_customers` |
| 🧾 مزامنة الطلبات               | `POST`    | `/method/integration_hub.api.sync_orders` |
| 📤 إرسال الطلبات للمتجر        | `POST`    | `/method/integration_hub.api.send_orders` |
| 📦 جلب بيانات المخزون          | `GET`     | `/method/integration_hub.api.get_inventory` |
| 🔢 إجمالي عدد المنتجات في المخزون | `GET`     | `/method/integration_hub.api.get_inventory/total` |
| ⚙️ إعدادات المتجر              | `GET`     | `/method/integration_hub.api.get_store_settings` |

---

## ⚙️ التنصيب داخل Frappe

```bash
# داخل مجلد frappe-bench
cd apps
git clone https://github.com/MohammedAl-sultani/sync_integration_erpnext.git integration_hub

# ثم أضف التطبيق
cd ..
bench --site site1.local install-app integration_hub
🔄 تحديث واجهة Swagger
بعد أي تعديل على swagger.json:


bench build
bench --site site1.local clear-cache
🛠️ ملفات مهمة
swagger.json: توثيق الواجهات (المسار: integration_hub/public/swagger/)

integration_store.py: يحتوي دوال sync_now وواجهات الربط

api/inventory.py: نقاط API الخارجية لجلب بيانات المخزون بعد التصفية

📜 الرخصة
مشروع مفتوح المصدر — يمكنك استخدامه بحرية في المشاريع التجارية والشخصية.

👤 المطور
تم التطوير بواسطة: محمد السلطاني

إذا أعجبك المشروع ⭐ فلا تنسَ دعمه على GitHub.



هل ترغب أن أرفق معه أيضًا مثال بصيغة `curl` لتجربة أحد الطلبات مباشرة من الطرفية؟
