frappe.ui.form.on('Poultry Batch', {
    setup: function (frm) {
        frappe.db.get_single_value('Poultry Farm Settings', 'item_group').then(val => {
            if (val) {
                frm.set_query('live_bird_item', function () {
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
