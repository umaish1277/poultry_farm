import frappe
from frappe.utils import flt, getdate

def get_context(context):
    context.no_cache = 1
    
    # Get active batches with projected dates
    batches = frappe.get_all("Poultry Batch", 
        fields=["name", "shed", "breed", "projected_harvest_date", "initial_count", "start_date"],
        filters={"status": "Active", "projected_harvest_date": [">=", getdate()]},
        order_by="projected_harvest_date asc"
    )
    
    for batch in batches:
        # Calculate current availability (approximate)
        # Mortality + Culls
        stats = frappe.db.sql("""
            SELECT SUM(mortality) + SUM(culls) as loss
            FROM `tabDaily Flock Entry`
            WHERE poultry_batch = %s AND docstatus < 2
        """, batch.name, as_dict=1)[0]
        
        # Already harvested
        harvested = frappe.db.sql("""
            SELECT SUM(qty) as harvested
            FROM `tabLive Bird Harvesting`
            WHERE poultry_batch = %s AND docstatus == 1
        """, batch.name, as_dict=1)[0]
        
        loss = flt(stats.loss) if stats.loss else 0
        h_qty = flt(harvested.harvested) if harvested.harvested else 0
        
        batch.available_qty = int(batch.initial_count - loss - h_qty)
        batch.farm = frappe.db.get_value("Poultry Shed", batch.shed, "poultry_farm")
        
    context.batches = batches
