# Copyright (c) 2024, Umaish Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PoultryFarm(Document):
	def validate(self):
		if not self.company:
			self.company = frappe.db.get_single_value("Poultry Farm Settings", "company")
		
		if not self.company:
			frappe.throw(_("Please set the Default Company in Poultry Farm Settings before creating a Farm."))
