# Copyright (c) 2023, earthians and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OilLabTest(Document):
	def on_update(self):
		if self.referance_type=='Purchase Receipt':
			if self.voucher_no:				
				if not frappe.db.get_value('Purchase Receipt',{'name':self.voucher_no},'docstatus'):
					net_weight=frappe.db.get_value('Purchase Receipt',{'name':self.voucher_no},'net_weight') or 0
					qty_in_litters=0
					density_per_sg=self.density_per_sg or 0
					flash_point=self.flash_point or 0
					water_contant=self.water_contant or 0
					if net_weight and density_per_sg:
						qty_in_litters=float(net_weight)/float(density_per_sg)
					frappe.db.set_value('Purchase Receipt',self.voucher_no,{'density_per_sg':density_per_sg,'flash_point':flash_point,'water_contant':water_contant,'qty_in_litters':qty_in_litters})
				else:
					frappe.throw("You cannot update Test report, Purchase Receipt is already submitted")
		else:
			if self.voucher_no:
				if not frappe.db.get_value('Delivery Note',{'name':self.voucher_no},'docstatus'):
					net_weight=frappe.db.get_value('Delivery Note',{'name':self.voucher_no},'net_weight') or 0
					qty_in_litters=0
					density_per_sg=self.density_per_sg or 0
					flash_point=self.flash_point or 0
					water_contant=self.water_contant or 0
					if net_weight and density_per_sg:
						qty_in_litters=float(net_weight)/float(density_per_sg)				
					frappe.db.set_value('Delivery Note',self.voucher_no,{'density_per_sg':density_per_sg,'flash_point':flash_point,'water_contant':water_contant,'qty_in_litters':qty_in_litters})
				else:
					frappe.throw("You cannot update Test report, Delivery Note is already submitted")

@frappe.whitelist()
def update_test_purchase(doc, method):
	if doc.company=='Dure Oil Middle East Factory - Sole Proprietorship LLC':
		lbrest=frappe.db.get_value('Oil Lab Test',{'voucher_no':doc.name,'referance_type':'Purchase Receipt'},'name')
		if doc.docstatus=='0':
			if lbrest:
				tdoc=frappe.get_doc("Oil Lab Test", lbrest)
				tdoc.tickect_no=doc.tickect_no			
				tdoc.party_type='Supplier'
				tdoc.party=doc.supplier
				tdoc.save()
			else:
				tdoc=frappe.new_doc("Oil Lab Test")
				tdoc.tickect_no=doc.tickect_no
				tdoc.referance_type='Purchase Receipt'
				tdoc.voucher_no=doc.name
				tdoc.party_type='Supplier'
				tdoc.party=doc.supplier
				tdoc.save()
				frappe.db.set_value('Purchase Receipt',doc.name,{'ltr_no':tdoc.name})

		

@frappe.whitelist()
def update_test_delivary(doc, method):
	if doc.company=='Dure Oil Middle East Factory - Sole Proprietorship LLC':
		lbrest=frappe.db.get_value('Oil Lab Test',{'voucher_no':doc.name,'referance_type':'Delivery Note'},'name')
		if doc.docstatus=='0':
			if lbrest:
				tdoc=frappe.get_doc("Oil Lab Test", lbrest)
				tdoc.tickect_no=doc.tickect_no			
				tdoc.party_type='Customer'
				tdoc.party=doc.customer
				tdoc.save()
				
			else:
				tdoc=frappe.new_doc("Oil Lab Test")
				tdoc.tickect_no=doc.tickect_no
				tdoc.referance_type='Delivery Note'
				tdoc.voucher_no=doc.name
				tdoc.party_type='Customer'
				tdoc.party=doc.customer
				tdoc.save()
				frappe.db.set_value('Delivery Note',doc.name,{'ltr_no':tdoc.name})

		