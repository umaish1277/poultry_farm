# Copyright (c) 2024, Umaish Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PoultryBatch(Document):
	def validate(self):
		if not self.company:
			self.company = frappe.db.get_single_value("Poultry Farm Settings", "company")
		
		if not self.company:
			frappe.throw(_("Please set the Default Company in Poultry Farm Settings before creating a Batch."))
	
	def on_update(self):
		if self.vaccination_template:
			self.generate_vaccination_schedule()

	def generate_vaccination_schedule(self):
		template = frappe.get_doc("Vaccination Template", self.vaccination_template)
		from frappe.utils import add_days, getdate
		
		for item in template.items:
			scheduled_date = add_days(getdate(self.start_date), item.day_number)
			
			# Check if this specific vaccine + batch + date combination exists
			if not frappe.db.exists("Poultry Vaccination Schedule", {
				"poultry_batch": self.name,
				"vaccine": item.vaccine,
				"scheduled_date": scheduled_date
			}):
				sch = frappe.get_doc({
					"doctype": "Poultry Vaccination Schedule",
					"poultry_batch": self.name,
					"vaccine": item.vaccine,
					"scheduled_date": scheduled_date,
					"status": "Pending",
					"company": self.company,
					"naming_series": "PVS-.#####"
				})
				sch.insert()
