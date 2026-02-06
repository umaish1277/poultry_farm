import frappe

def get_permission_query_conditions(user=None):
    if not user: user = frappe.session.user
    
    # If user is System Manager, they might still want to see everything?
    # But the request says "tag this app to a single company"
    # So we force the filter from Poultry Farm Settings
    
    company = frappe.db.get_single_value("Poultry Farm Settings", "company")
    if company:
        return f"company = '{company}'"
    return ""

def propagate_poultry_batch(doc, method=None):
    if hasattr(doc, "poultry_batch") and doc.poultry_batch:
        return

    if not doc.get("voucher_no") or not doc.get("voucher_type"):
        return

    poultry_batch = None
    
    # 1. Try parent document first
    try:
        if frappe.get_meta(doc.voucher_type).has_field("poultry_batch"):
            poultry_batch = frappe.db.get_value(doc.voucher_type, doc.voucher_no, "poultry_batch")
    except Exception:
        pass

    # 2. If not found and it is a GL Entry, check the source child row (for Journal Entry)
    if not poultry_batch and doc.doctype == "GL Entry" and doc.get("voucher_detail_no"):
        if doc.voucher_type == "Journal Entry":
            poultry_batch = frappe.db.get_value("Journal Entry Account", doc.voucher_detail_no, "poultry_batch")
        elif doc.voucher_type == "Purchase Invoice":
             # If we want item level tagging, we could check Purchase Invoice Item
             pass

    if poultry_batch:
        doc.poultry_batch = poultry_batch

def update_batch_profitability(doc, method=None):
    if doc.get("poultry_batch"):
        try:
            batch = frappe.get_doc("Poultry Batch", doc.poultry_batch)
            batch.update_profitability()
        except Exception:
            # Avoid blocking GL entry creation if batch update fails
            pass
