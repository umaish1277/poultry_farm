frappe.ui.form.on('Daily Flock Entry', {
    setup: function (frm) {
        frappe.db.get_single_value('Poultry Farm Settings', 'item_group').then(val => {
            if (val) {
                frm.set_query('item_code', 'items', function () {
                    return {
                        filters: [
                            ['Item', 'item_group', '=', val]
                        ]
                    };
                });
            }
        });
    }
});
