import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "GL Entry": [
            {
                "fieldname": "poultry_batch",
                "label": "Poultry Batch",
                "fieldtype": "Link",
                "options": "Poultry Batch",
                "insert_after": "party",
                "in_list_view": 1,
                "in_standard_filter": 1
            }
        ],
        "Stock Ledger Entry": [
            {
                "fieldname": "poultry_batch",
                "label": "Poultry Batch",
                "fieldtype": "Link",
                "options": "Poultry Batch",
                "insert_after": "batch_no",
                "in_list_view": 1,
                "in_standard_filter": 1
            }
        ],
        "Purchase Invoice": [
            {
                "fieldname": "poultry_batch",
                "label": "Poultry Batch",
                "fieldtype": "Link",
                "options": "Poultry Batch",
                "insert_after": "project"
            }
        ],
        "Journal Entry Account": [
            {
                "fieldname": "poultry_batch",
                "label": "Poultry Batch",
                "fieldtype": "Link",
                "options": "Poultry Batch",
                "insert_after": "reference_name"
            }
        ]
    }

    create_custom_fields(custom_fields)
    frappe.db.commit()
    print("Successfully added custom fields for Poultry Batch.")

if __name__ == "__main__":
    execute()
