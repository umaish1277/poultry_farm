import frappe
import json
from frappe import _
from frappe.model.document import Document

class LiveBirdHarvesting(Document):
	def validate(self):
		if not self.company:
			self.company = frappe.db.get_single_value("Poultry Farm Settings", "company")
		self.calculate_amount()

	def calculate_amount(self):
		self.amount = flt(self.weight) * flt(self.valuation_rate)

	def on_submit(self):
		self.create_stock_entry()
		self.create_sales_invoice()

	def on_cancel(self):
		if self.stock_entry:
			se = frappe.get_doc("Stock Entry", self.stock_entry)
			if se.docstatus == 1:
				se.cancel()
		
		if self.sales_invoice:
			si = frappe.get_doc("Sales Invoice", self.sales_invoice)
			if si.docstatus == 1:
				si.cancel()

	def create_stock_entry(self):
		# Get Warehouse from Farm
		farm_warehouse = frappe.db.get_value("Poultry Farm", self.poultry_farm, "warehouse")
		if not farm_warehouse:
			frappe.throw(_("Please set a warehouse for the Poultry Farm {0}").format(self.poultry_farm))

		# Get ERPNext Batch from Poultry Batch
		erp_batch = frappe.db.get_value("Poultry Batch", self.poultry_batch, "erpnext_batch")
		
		# If no batch, create one if the item is batch-tracked
		is_batch_tracked = frappe.db.get_value("Item", self.item, "has_batch_no")
		
		if is_batch_tracked and not erp_batch:
			erp_batch = self.create_erp_batch()

		se = frappe.get_doc({
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Receipt",
			"posting_date": self.posting_date,
			"company": self.company,
			"items": [
				{
					"item_code": self.item,
					"t_warehouse": farm_warehouse,
					"qty": self.qty,
					"uom": frappe.db.get_value("Item", self.item, "stock_uom"),
					"basic_rate": (flt(self.weight) * flt(self.valuation_rate)) / flt(self.qty) if self.qty else 0,
					"batch_no": erp_batch
				}
			]
		})
		se.insert()
		se.submit()
		
		self.db_set("stock_entry", se.name)
		
	def create_sales_invoice(self):
		si = frappe.get_doc({
			"doctype": "Sales Invoice",
			"customer": self.customer,
			"company": self.company,
			"posting_date": self.posting_date,
			"due_date": self.posting_date,
			"update_stock": 0,
			"poultry_batch": self.poultry_batch,
			"items": [
				{
					"item_code": self.item,
					"qty": self.weight,
					"rate": self.valuation_rate,
					"uom": frappe.db.get_value("Item", self.item, "stock_uom"), # Might need 'Kg' specifically
					"warehouse": frappe.db.get_value("Poultry Farm", self.poultry_farm, "warehouse")
				}
			]
		})
		si.insert()
		si.submit()
		self.db_set("sales_invoice", si.name)

	def create_erp_batch(self):
		batch = frappe.get_doc({
			"doctype": "Batch",
			"item": self.item,
			"batch_id": self.poultry_batch # Use Poultry Batch ID as the Batch ID
		})
		batch.insert()
		
		# Update Poultry Batch with the new ERPNext Batch
		frappe.db.set_value("Poultry Batch", self.poultry_batch, "erpnext_batch", batch.name)
		
		return batch.name

def flt(val):
	from frappe.utils import flt as _flt
	return _flt(val)
