import frappe
from frappe.modules.import_file import import_file_by_path
import os

def sync():
    charts = [
        'mortality_trend', 
        'egg_production_trend', 
        'feed_consumption_trend', 
        'harvesting_trend', 
        'harvesting_weight_trend'
    ]
    
    app_path = frappe.get_app_path('poultry_farm')
    print(f"App path: {app_path}")
    
    for c in charts:
        folder_name = c
        file_name = c + '.json'
        path = os.path.join(app_path', 'poultry_farm', 'dashboard_chart', folder_name, file_name)
        # Wait, another typo potential. I'll be very careful.
