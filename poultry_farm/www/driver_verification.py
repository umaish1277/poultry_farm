import frappe
from frappe import _

def get_context(context):
    harvest_id = frappe.form_dict.get("id")
    if not harvest_id:
        frappe.respond_as_web_page(_("Invalid Request"), _("No Harvest ID provided."), http_status_code=404)
        return

    try:
        harvest = frappe.get_doc("Live Bird Harvesting", harvest_id)
        if harvest.docstatus != 1:
            frappe.respond_as_web_page(_("Invalid Status"), _("This harvest record is not submitted."), http_status_code=403)
            return
            
        context.harvest = harvest
        context.title = _("Driver Verification: {0}").format(harvest_id)
    except frappe.DoesNotExistError:
        frappe.respond_as_web_page(_("Not Found"), _("Harvest record not found."), http_status_code=404)

@frappe.whitelist(allow_guest=True)
def confirm_load(harvest_id, driver_name, vehicle_no):
    try:
        doc = frappe.get_doc("Live Bird Harvesting", harvest_id)
        doc.db_set("driver_name", driver_name)
        doc.db_set("vehicle_no", vehicle_no)
        doc.db_set("driver_verification_status", "Confirmed")
        doc.db_set("driver_verified_at", frappe.utils.now_datetime())
        return {"status": "success", "message": _("Load confirmed successfully.")}
    except Exception as e:
        return {"status": "error", "message": str(e)}
