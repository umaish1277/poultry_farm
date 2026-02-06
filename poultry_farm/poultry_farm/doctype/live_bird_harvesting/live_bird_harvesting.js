frappe.ui.form.on('Live Bird Harvesting', {
    setup: function (frm) {
        frappe.db.get_single_value('Poultry Farm Settings', 'item_group').then(val => {
            if (val) {
                frm.set_query('item', function () {
                    return {
                        filters: [
                            ['Item', 'item_group', '=', val]
                        ]
                    };
                });
            }
        });

        frappe.db.get_single_value('Poultry Farm Settings', 'customer_group').then(val => {
            if (val) {
                frm.set_query('customer', function () {
                    return {
                        filters: [
                            ['Customer', 'customer_group', '=', val]
                        ]
                    };
                });
            }
        });
    }
});
