# Copyright (c) 2024, Umaish Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DailyFlockEntry(Document):
	def validate(self):
		if not self.company:
			self.company = frappe.db.get_single_value("Poultry Farm Settings", "company")
		self.calculate_fcr()

	def on_submit(self):
		self.calculate_fcr() # Recalculate as items might have changed
		self.check_fcr_deviation()
		self.create_stock_entries()

	def calculate_fcr(self):
		if not self.average_weight or not self.batch:
			return

		batch_doc = frappe.get_doc("Poultry Batch", self.batch)
		
		# Previous total feed (cumulative)
		from frappe.utils import flt
		prev_feed_kg = flt(frappe.db.sql("""
			SELECT SUM(item.qty) 
			FROM `tabDaily Flock Entry Item` item
			JOIN `tabDaily Flock Entry` parent ON item.parent = parent.name
			WHERE parent.batch = %s 
			AND parent.docstatus < 2
			AND parent.entry_date < %s
			AND item.purpose = 'Feed'
		""", (self.batch, self.entry_date))[0][0])
		
		current_feed_kg = sum([flt(item.qty) for item in self.items if item.purpose == 'Feed'])
		total_feed_kg = prev_feed_kg + current_feed_kg
		total_feed_g = total_feed_kg * 1000 # Standardizing to grams for comparison with breed standards
		
		# Previous total mortality/culls (cumulative)
		mort_cull_data = frappe.db.sql("""
			SELECT SUM(mortality), SUM(culls)
			FROM `tabDaily Flock Entry`
			WHERE batch = %s AND entry_date < %s AND docstatus < 2
		""", (self.batch, self.entry_date))[0]
		
		prev_mortality = flt(mort_cull_data[0])
		prev_culls = flt(mort_cull_data[1])
		
		total_mortality = prev_mortality + flt(self.mortality)
		total_culls = prev_culls + flt(self.culls)
		
		actual_birds = flt(batch_doc.initial_count) - total_mortality - total_culls
		
		if actual_birds > 0 and flt(self.average_weight) > 0:
			total_live_weight_g = actual_birds * flt(self.average_weight)
			self.fcr = flt(total_feed_g / total_live_weight_g)

	def check_fcr_deviation(self):
		if not self.fcr or not self.batch:
			return
			
		batch_doc = frappe.get_doc("Poultry Batch", self.batch)
		if not batch_doc.breed:
			return
			
		from frappe.utils import date_diff, getdate, flt
		# Age calculation
		age = date_diff(getdate(self.entry_date), getdate(batch_doc.start_date)) + 1
		
		# Fetch standard FCR for this age
		std_fcr = flt(frappe.db.get_value("Poultry Breed Standard Item", 
			{"parent": batch_doc.breed, "day_number": age}, "std_fcr"))
		
		if std_fcr > 0 and self.fcr > (std_fcr * 1.1): # 10% deviation
			self.trigger_early_warning_alert(age, std_fcr)

	def trigger_early_warning_alert(self, age, std_fcr):
		msg = f"FCR Alert: Batch {self.batch} at Day {age} is deviating from breed standards. Actual: {self.fcr:.3f}, Standard: {std_fcr:.3f}."
		
		# Find System Managers
		users = frappe.get_all("Has Role", filters={"role": "System Manager"}, pluck="parent")
		
		for user in users:
			if frappe.db.exists("User", user):
				frappe.get_doc({
					"doctype": "Notification Log",
					"for_user": user,
					"subject": f"FCR Warning: {self.batch}",
					"email_content": msg,
					"type": "Alert",
					"document_type": "Daily Flock Entry",
					"document_link": self.name
				}).insert(ignore_permissions=True)

	def create_stock_entries(self):
		# Fetch Farm Warehouse
		farm_doc = frappe.get_doc("Poultry Farm", self.farm)
		warehouse = farm_doc.warehouse

		if not warehouse:
			frappe.throw(f"Please link a Warehouse to Farm {self.farm} to process Stock Entries")

		issue_items = []
		receipt_items = []

		for item in self.items:
			if item.purpose in ["Feed", "Medicine"]:
				issue_items.append(item)
			elif item.purpose == "Egg Collection":
				receipt_items.append(item)

		if issue_items:
			self.make_stock_entry("Material Issue", warehouse, None, issue_items)
		
		if receipt_items:
			self.make_stock_entry("Material Receipt", None, warehouse, receipt_items)

	def make_stock_entry(self, entry_type, source, target, items):
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = entry_type
		se.from_warehouse = source
		se.to_warehouse = target
		se.company = self.company
		se.poultry_batch = self.batch
		se.posting_date = self.entry_date
		
		# Add Description link
		se.add_comment("Comment", f"Auto-generated from Daily Flock Entry {self.name}")

		for item in items:
			row = se.append("items", {})
			row.item_code = item.item_code
			row.qty = item.qty
			row.uom = item.uom
			if source: row.s_warehouse = source
			if target: row.t_warehouse = target
			# Cost Center? Fetch from Farm
			farm_doc = frappe.get_cached_doc("Poultry Farm", self.farm)
			if farm_doc.cost_center:
				row.cost_center = farm_doc.cost_center

		se.insert()
		se.submit()
		frappe.msgprint(f"Created {entry_type}: {se.name}")
