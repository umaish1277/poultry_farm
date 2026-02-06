import frappe
from frappe.modules.import_file import import_file_by_path
import os

def sync():
    # Charts to sync
    charts = [
        'mortality_trend', 
        'egg_production_trend', 
        'feed_consumption_trend', 
        'harvesting_trend', 
        'harvesting_weight_trend'
    ]
    
    app_path = frappe.get_app_path('poultry_farm')
    
    for c in charts:
        folder_name = c
        file_name = c + '.json'
        path = os.path.join(app_path, 'poultry_farm', 'dashboard_chart', folder_name, file_name)
        
        if os.path.exists(path):
            print(f"Syncing {c} from {path}")
            import_file_by_path(path, force=True)
            
            # Map chart name to record name (usually the same or Title Case)
            # Try to get the chart name from JSON if possible, or assume Title Case
            char_title = c.replace('_', ' ').title()
            
            # Find the chart record
            chart_doc_name = frappe.db.get_value('Dashboard Chart', {'chart_name': char_title}, 'name')
            if not chart_doc_name:
                 # Try matching by name directly
                 chart_doc_name = frappe.db.get_value('Dashboard Chart', char_title, 'name')
            
            if chart_doc_name:
                frappe.db.set_value('Dashboard Chart', chart_doc_name, {
                    'is_standard': 1,
                    'is_public': 1,
                    'owner': 'Administrator'
                })
                print(f"Updated metadata for chart: {chart_doc_name}")
            else:
                print(f"Could not find chart record for {char_title}")
        else:
            print(f"Path not found: {path}")

    # Sync Workspace
    workspace_path = os.path.join(app_path, 'poultry_farm', 'workspace', 'poultry_dashboard', 'poultry_dashboard.json')
    if os.path.exists(workspace_path):
        print(f"Syncing Workspace from {workspace_path}")
        import_file_by_path(workspace_path, force=True)
        frappe.db.set_value('Workspace', 'Poultry Dashboard', {
            'public': 1,
            'is_standard': 1 # Even if not in DocType, setting it might help in some versions or be ignored
        })
    
    frappe.db.commit()
    print("Done")

if __name__ == "__main__":
    sync()
