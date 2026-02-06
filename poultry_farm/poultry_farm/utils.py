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
