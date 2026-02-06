# Copyright (c) 2024, Umaish Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DailyFlockEntry(Document):
	def validate(self):
		if not self.company:
			self.company = frappe.db.get_single_value("Poultry Farm Settings", "company")
	def on_submit(self):
		self.create_stock_entries()

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
