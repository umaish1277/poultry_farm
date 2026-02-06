frappe.ui.form.on('Live Bird Harvesting', {
    refresh: function (frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Copy Driver Link'), function () {
                let url = window.location.origin + '/driver_verification?id=' + frm.doc.name;
                frappe.utils.copy_to_clipboard(url);
                frappe.show_alert({ message: __('Driver Link copied to clipboard'), indicator: 'green' });
            }, __('Logistics'));

            frm.add_custom_button(__('Open Driver Portal'), function () {
                let url = window.location.origin + '/driver_verification?id=' + frm.doc.name;
                window.open(url);
            }, __('Logistics'));
        }
    }
});
