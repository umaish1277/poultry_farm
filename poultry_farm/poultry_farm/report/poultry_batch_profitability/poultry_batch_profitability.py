import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": _("Batch"), "fieldname": "poultry_batch", "fieldtype": "Link", "options": "Poultry Batch", "width": 150},
		{"label": _("Breed"), "fieldname": "breed", "fieldtype": "Link", "options": "Poultry Breed Standard", "width": 120},
		{"label": _("Revenues"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
		{"label": _("Direct Costs"), "fieldname": "direct_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Overheads"), "fieldname": "overhead", "fieldtype": "Currency", "width": 120},
		{"label": _("Total Expense"), "fieldname": "total_expense", "fieldtype": "Currency", "width": 120},
		{"label": _("Net Profit"), "fieldname": "net_profit", "fieldtype": "Currency", "width": 120},
		{"label": _("ROI %"), "fieldname": "roi", "fieldtype": "Percent", "width": 100}
	]

def get_data(filters):
	conditions = ""
	if filters.get("company"):
		conditions += f" AND gle.company = '{filters.get('company')}'"
	if filters.get("poultry_batch"):
		conditions += f" AND gle.poultry_batch = '{filters.get('poultry_batch')}'"

	gl_entries = frappe.db.sql(f"""
		SELECT 
			gle.poultry_batch as poultry_batch,
			acc.root_type as root_type,
			acc.account_name as account_name,
			SUM(gle.credit - gle.debit) as balance,
			pb.breed as breed
		FROM `tabGL Entry` gle
		JOIN `tabAccount` acc ON gle.account = acc.name
		JOIN `tabPoultry Batch` pb ON gle.poultry_batch = pb.name
		WHERE gle.is_cancelled = 0 AND gle.poultry_batch IS NOT NULL AND gle.poultry_batch != ''
		{conditions}
		GROUP BY gle.poultry_batch, acc.root_type, acc.account_name
	""", as_dict=1)

	batch_data = {}

	for row in gl_entries:
		batch = row.poultry_batch
		if batch not in batch_data:
			batch_data[batch] = {
				"poultry_batch": batch,
				"breed": row.breed,
				"revenue": 0,
				"direct_cost": 0,
				"overhead": 0,
				"total_expense": 0,
				"net_profit": 0,
				"roi": 0
			}

		amount = flt(row.balance)
		
		if row.root_type == "Income":
			# Income is credit (positive balance)
			batch_data[batch]["revenue"] += amount
		elif row.root_type == "Expense":
			# Expenses are debit (negative balance in this query credit-debit)
			# We want to represent expense as positive in the report columns
			exp_amount = abs(amount)
			
			# Simple categorization
			lower_acc = row.account_name.lower()
			if any(x in lower_acc for x in ["feed", "medicine", "vaccine", "chick", "bird"]):
				batch_data[batch]["direct_cost"] += exp_amount
			else:
				batch_data[batch]["overhead"] += exp_amount
			
			batch_data[batch]["total_expense"] += exp_amount

	# Final calculations
	result = []
	for batch, values in batch_data.items():
		values["net_profit"] = values["revenue"] - values["total_expense"]
		if values["total_expense"] > 0:
			values["roi"] = (values["net_profit"] / values["total_expense"]) * 100
		
		result.append(values)

	return result
