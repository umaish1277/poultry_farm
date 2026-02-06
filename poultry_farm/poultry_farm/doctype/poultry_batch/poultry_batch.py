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
		
		self.calculate_projections()
	
	def calculate_projections(self):
		if self.breed and self.start_date:
			std_age = frappe.db.get_value("Poultry Breed Standard", self.breed, "standard_harvest_age")
			if std_age:
				from frappe.utils import add_days, getdate
				self.projected_harvest_date = add_days(getdate(self.start_date), int(std_age))
	
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

	def update_profitability(self):
		from frappe.utils import flt
		
		# Sum of Income (Credit - Debit)
		gl_data = frappe.db.sql("""
			SELECT 
				acc.root_type as root_type,
				SUM(gle.credit - gle.debit) as balance
			FROM `tabGL Entry` gle
			JOIN `tabAccount` acc ON gle.account = acc.name
			WHERE gle.poultry_batch = %s AND gle.is_cancelled = 0
			GROUP BY acc.root_type
		""", self.name, as_dict=1)
		
		revenue = 0
		expense = 0
		
		for row in gl_data:
			if row.root_type == "Income":
				revenue += flt(row.balance)
			elif row.root_type == "Expense":
				expense += abs(flt(row.balance))
				
		self.net_profit = flt(revenue - expense)
		if expense > 0:
			self.roi = flt((self.net_profit / expense) * 100)
		else:
			self.roi = 0
			
		self.db_set("net_profit", self.net_profit)
		self.db_set("roi", self.roi)
		self.db_set("status", self.status) # Ensure other fields are synced if needed, but db_set is fine for specific ones
