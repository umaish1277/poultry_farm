import frappe
from frappe.utils import getdate, today
from frappe import _

def daily():
	send_vaccination_reminders()

def send_vaccination_reminders():
	"""Send notifications for vaccinations due today"""
	due_today = frappe.get_all("Poultry Vaccination Schedule", 
		filters={
			"scheduled_date": today(),
			"status": "Pending"
		},
		fields=["name", "poultry_batch", "vaccine", "company"]
	)
	
	for entry in due_today:
		# Create a system notification
		notification_message = _("Vaccination/Medication '{0}' is due today for Batch {1}").format(
			entry.vaccine, entry.poultry_batch
		)
		
		# Get users with System Manager role or anyone you want to notify
		users = frappe.get_all("Has Role", filters={"role": "System Manager"}, fields=["parent"])
		
		for user in users:
			frappe.publish_realtime(
				"msgprint", 
				{"message": notification_message, "title": _("Vaccination Reminder"), "indicator": "orange"},
				user=user.parent
			)
			
			# Also create a ToDo for visibility
			if not frappe.db.exists("ToDo", {"reference_type": "Poultry Vaccination Schedule", "reference_name": entry.name}):
				frappe.get_doc({
					"doctype": "ToDo",
					"description": notification_message,
					"reference_type": "Poultry Vaccination Schedule",
					"reference_name": entry.name,
					"allocated_to": user.parent,
					"assigned_by": "Administrator"
				}).insert(ignore_permissions=True)
