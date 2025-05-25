frappe.ui.form.on('Integration Store', {
    refresh: function(frm) {
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('مزامنة الآن'), function() {
                frappe.call({
                    method: 'integration_hub.integration_hub.doctype.integration_store.integration_store.run_sync_now',
                    args: {
                        doc: frm.doc
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint(__('تم تنفيذ أمر المزامنة.'));
                        }
                    }
                });
            });
        }
    }
});
