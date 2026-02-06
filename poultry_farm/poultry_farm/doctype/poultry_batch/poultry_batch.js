frappe.ui.form.on('Poultry Batch', {
    refresh: function (frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('View Harvest Projections'), function () {
                window.open('/harvest_projections');
            });
        }
    }
});
