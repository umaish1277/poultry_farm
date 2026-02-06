import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def log_sensor_reading(sensor_id, value):
    try:
        # 1. Fetch Sensor
        if not frappe.db.exists("Poultry Sensor", sensor_id):
            return {"status": "error", "message": "Sensor not found"}
        
        sensor = frappe.get_doc("Poultry Sensor", sensor_id)
        value = float(value)
        
        # 2. Create Reading
        reading = frappe.get_doc({
            "doctype": "Poultry Sensor Reading",
            "sensor": sensor.name,
            "reading_value": value,
            "reading_time": frappe.utils.now_datetime()
        })
        reading.insert(ignore_permissions=True)
        
        # 3. Update Sensor Last Value
        sensor.db_set("last_value", value)
        sensor.db_set("last_seen", frappe.utils.now_datetime())
        
        # 4. Check Thresholds
        check_expectations(sensor, value)
        
        return {"status": "success", "reading_id": reading.name}
    except Exception as e:
        frappe.log_error(f"Sensor Log Error: {str(e)}")
        return {"status": "error", "message": str(e)}

def check_expectations(sensor, value):
    thresholds = frappe.get_all("Environmental Threshold",
        filters={
            "shed": sensor.shed,
            "parameter": sensor.parameter,
            "status": "Active"
        },
        fields=["name", "min_value", "max_value", "alert_action", "email_template"]
    )
    
    for t in thresholds:
        alert_triggered = False
        msg = ""
        
        if t.min_value is not None and value < t.min_value:
            alert_triggered = True
            msg = f"Low {sensor.parameter} Alert! Current: {value}{sensor.unit or ''} (Min: {t.min_value})"
            
        elif t.max_value is not None and value > t.max_value:
            alert_triggered = True
            msg = f"High {sensor.parameter} Alert! Current: {value}{sensor.unit or ''} (Max: {t.max_value})"
            
        if alert_triggered:
            trigger_action(t, sensor, msg)

def trigger_action(threshold, sensor, message):
    action = threshold.alert_action
    
    if action == "Email Alert":
        # Send to System Managers
        recipients = frappe.get_all("Has Role", filters={"role": "System Manager"}, pluck="parent")
        frappe.sendmail(
            recipients=recipients,
            subject=f"⚠️ {sensor.shed} Environment Alert",
            message=message
        )
    
    # Log the alert (System Notification)
    frappe.get_doc({
        "doctype": "Notification Log",
        "subject": f"Environment Alert: {sensor.shed}",
        "email_content": message,
        "type": "Alert",
        "document_type": "Poultry Sensor",
        "document_name": sensor.name
    }).insert(ignore_permissions=True)
