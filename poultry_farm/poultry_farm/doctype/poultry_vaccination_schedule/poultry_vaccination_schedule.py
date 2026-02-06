# Copyright (c) 2024, Umaish Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate

class PoultryVaccinationSchedule(Document):
	def validate(self):
		if not self.company:
			self.company = frappe.db.get_single_value("Poultry Farm Settings", "company")
		
		if self.status == "Administered" and not self.administered_date:
			self.administered_date = frappe.utils.today()
		
		if self.status == "Administered" and not self.administered_by:
			self.administered_by = frappe.session.user

	def on_submit(self):
		if self.status != "Administered":
			frappe.throw(_("Please set status to 'Administered' before submitting."))
