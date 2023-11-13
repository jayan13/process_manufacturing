# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
import erpnext
from frappe import _
from erpnext.stock.doctype.batch.batch import get_batch_no, get_batch_qty, set_batch_nos
from frappe.utils import cint, comma_or, cstr, flt, format_time, formatdate, getdate, nowdate
from erpnext.controllers.stock_controller import StockController
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from frappe.model.document import Document


class FinishedGoodError(frappe.ValidationError):
	pass

class CustomStockEntry(StockEntry):
	

	def validate(self):
		self.pro_doc = frappe._dict()
		if self.work_order:
			self.pro_doc = frappe.get_doc("Work Order", self.work_order)
		#print("\n\n\n hooks Values are being validated! \n\n\n")
		self.validate_posting_time()
		self.validate_purpose()
		self.validate_item()
		self.validate_customer_provided_item()
		self.validate_qty()
		self.set_transfer_qty()
		self.validate_uom_is_integer("uom", "qty")
		self.validate_uom_is_integer("stock_uom", "transfer_qty")
		self.validate_warehouse()
		self.validate_work_order()
		self.validate_bom()

		if self.purpose in ("Manufacture", "Repack"):
			self.mark_finished_and_scrap_items()
			self.validate_finished_goods()

		self.validate_with_material_request()
		self.validate_batch()
		self.validate_inspection()
		self.validate_fg_completed_qty()
		self.validate_difference_account()
		self.set_job_card_data()
		self.set_purpose_for_stock_entry()
		self.clean_serial_nos()
		self.validate_duplicate_serial_no()

		if not self.from_bom:
			self.fg_completed_qty = 0.0

		if self._action == "submit":
			self.make_batches("t_warehouse")
		else:
			set_batch_nos(self, "s_warehouse")

		self.validate_serialized_batch()
		self.set_actual_qty()
		self.calculate_rate_and_amount()
		self.validate_putaway_capacity()

		if not self.get("purpose") == "Manufacture":
			# ignore scrap item wh difference and empty source/target wh
			# in Manufacture Entry
			self.reset_default_field_value("from_warehouse", "items", "s_warehouse")
			self.reset_default_field_value("to_warehouse", "items", "t_warehouse")

	

	def validate_finished_goods(self):
		"""
		1. Check if FG exists (mfg, repack)
		2. Check if Multiple FG Items are present (mfg)
		3. Check FG Item and Qty against WO if present (mfg)
		"""
		production_item, wo_qty, finished_items = None, 0, []

		wo_details = frappe.db.get_value("Work Order", self.work_order, ["production_item", "qty"])
		if wo_details:
			production_item, wo_qty = wo_details

		for d in self.get("items"):
			if d.is_finished_item:
				if not self.work_order:
					# Independent MFG Entry/ Repack Entry, no WO to match against
					finished_items.append(d.item_code)
					continue

				if d.item_code != production_item:
					frappe.throw(
						_("Finished Item {0} does not match with Work Order {1}").format(
							d.item_code, self.work_order
						)
					)
				elif flt(d.transfer_qty) > flt(self.fg_completed_qty):
					frappe.throw(
						_("Quantity in row {0} ({1}) must be same as manufactured quantity {2}").format(
							d.idx, d.transfer_qty, self.fg_completed_qty
						)
					)

				finished_items.append(d.item_code)

		if not finished_items:
			frappe.throw(
				msg=_("There must be atleast 1 Finished Good in this Stock Entry").format(self.name),
				title=_("Missing Finished Good"),
				exc=FinishedGoodError,
			)

		if self.purpose == "Manufacture":
			#if len(set(finished_items)) > 1:
			#	frappe.throw(
			#		msg=_("Multiple items cannot be marked as finished item"),
			#		title=_("Note"),
			#		exc=FinishedGoodError,
			#	)

			allowance_percentage = flt(
				frappe.db.get_single_value(
					"Manufacturing Settings", "overproduction_percentage_for_work_order"
				)
			)
			allowed_qty = wo_qty + ((allowance_percentage / 100) * wo_qty)

			# No work order could mean independent Manufacture entry, if so skip validation
			if self.work_order and self.fg_completed_qty > allowed_qty:
				frappe.throw(
					_("For quantity {0} should not be greater than work order quantity {1}").format(
						flt(self.fg_completed_qty), wo_qty
					)
				)

	
