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
						item=frappe.db.get_value("Purchase Receipt Item",{'parent':self.voucher_no},['name','rate','qty'], as_dict=1)
						if item:
							if item.qty!=qty_in_litters:
								frappe.db.set_value('Purchase Receipt Item',item.name,{'qty':qty_in_litters,'received_qty':qty_in_litters})
								send_notification_to_user(self)
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
						item=frappe.db.get_value("Delivery Note Item",{'parent':self.voucher_no},['name','rate','qty'], as_dict=1)
						if item:
							if item.qty!=qty_in_litters:
								frappe.db.set_value('Delivery Note Item',item.name,{'qty':qty_in_litters})
								send_notification_to_user(self)
				else:
					frappe.throw("You cannot update Test report, Delivery Note is already submitted")

@frappe.whitelist()
def update_test_purchase(doc, method):
	
	if method=='on_update':
		if doc.company=='Dure Oil Middle East Factory - Sole Proprietorship LLC':
			lbrest=frappe.db.get_value('Oil Lab Test',{'voucher_no':doc.name,'referance_type':'Purchase Receipt'},'name')
			if not doc.docstatus and doc.tickect_no:
				if lbrest:
					tdoc=frappe.get_doc("Oil Lab Test", lbrest)
					if doc.supplier!=tdoc.party or tdoc.tickect_no!=doc.tickect_no:
						tdoc.tickect_no=doc.tickect_no	
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
					send_notification_to_lab(tdoc)
	else:
		if doc.company=='Dure Oil Middle East Factory - Sole Proprietorship LLC':
			if doc.tickect_no:
				tdoc=frappe.new_doc("Oil Lab Test")
				tdoc.tickect_no=doc.tickect_no
				tdoc.referance_type='Purchase Receipt'
				tdoc.voucher_no=doc.name
				tdoc.party_type='Supplier'
				tdoc.party=doc.supplier
				tdoc.save()
				frappe.db.set_value('Purchase Receipt',doc.name,{'ltr_no':tdoc.name})
				send_notification_to_lab(tdoc)
		

@frappe.whitelist()
def update_test_delivary(doc, method):
	if method=='on_update':
		if doc.company=='Dure Oil Middle East Factory - Sole Proprietorship LLC':
			lbrest=frappe.db.get_value('Oil Lab Test',{'voucher_no':doc.name,'referance_type':'Delivery Note'},'name')
			if not doc.docstatus and doc.tickect_no:
				if lbrest:
					tdoc=frappe.get_doc("Oil Lab Test", lbrest)
					if doc.customer!=tdoc.party or tdoc.tickect_no!=doc.tickect_no:
						tdoc.tickect_no=doc.tickect_no
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
					send_notification_to_lab(tdoc)
	else:
		if doc.company=='Dure Oil Middle East Factory - Sole Proprietorship LLC':
			if doc.tickect_no:
				tdoc=frappe.new_doc("Oil Lab Test")
				tdoc.tickect_no=doc.tickect_no
				tdoc.referance_type='Delivery Note'
				tdoc.voucher_no=doc.name
				tdoc.party_type='Customer'
				tdoc.party=doc.customer
				tdoc.save()
				frappe.db.set_value('Delivery Note',doc.name,{'ltr_no':tdoc.name})
				send_notification_to_lab(tdoc)
@frappe.whitelist()
def delete_test_purchase(doc, method):
	if doc.company=='Dure Oil Middle East Factory - Sole Proprietorship LLC':
		lbrest=frappe.db.get_value('Oil Lab Test',{'voucher_no':doc.name,'referance_type':'Purchase Receipt'},'name')
		if lbrest:
			tdoc=frappe.get_doc("Oil Lab Test", lbrest)
			tdoc.delete()

@frappe.whitelist()
def delete_test_delivary(doc, method):
	if doc.company=='Dure Oil Middle East Factory - Sole Proprietorship LLC':
		lbrest=frappe.db.get_value('Oil Lab Test',{'voucher_no':doc.name,'referance_type':'Delivery Note'},'name')
		if lbrest:
			tdoc=frappe.get_doc("Oil Lab Test", lbrest)
			tdoc.delete()

@frappe.whitelist()
def send_notification_to_lab(lab_test): 
	company=frappe.db.get_value(lab_test.referance_type,lab_test.voucher_no,'company')
	users=frappe.db.sql("""select user from `tabLab Notification Receivers` n left join `tabLab Test Notification Receivers` u on u.name=n.parent 
	where n.parentfield='lab_test_creation_notification_receivers' and u.company='{0}'""".format(company),as_dict=1)
	docn='oil-lab-test'
	for us in users:
		receiver,full_name=frappe.db.get_value('User', us.user, ['email','full_name'])
		url=frappe.utils.get_url()
		Email_Subject="""Lab Test Request For {0}. Ticket no: {1}""".format(lab_test.voucher_no,lab_test.tickect_no)
		pgurl='<a href="'+url+'/app/'+docn+'/'+lab_test.name+'" >'+lab_test.name+'</a>'
		#receiver='jayakumar@alantechnologies.net'
		msg=""" Dear {0}<br> 
						Lab Test Request created for {1}. Ticket No {2} Please click here {3}  <br> 
						""".format(full_name,lab_test.referance_type,lab_test.tickect_no,pgurl)
		if receiver:
			email_args = {
						"recipients": [receiver],
						"message": msg,
						"subject": Email_Subject,
						"reference_doctype": 'Oil Lab Test',
						"reference_name": lab_test.name
						}
			frappe.enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
		frappe.msgprint('Notification Email Send to '+full_name)

@frappe.whitelist()
def send_notification_to_user(lab_test):
	company=frappe.db.get_value(lab_test.referance_type,lab_test.voucher_no,'company')
	users=frappe.db.sql("""select user from `tabLab Notification Receivers` n left join `tabLab Test Notification Receivers` u on u.name=n.parent 
	where n.parentfield='lab_test_update_notification_receivers' and u.company='{0}'""".format(company),as_dict=1)
	docn=str(lab_test.referance_type).replace(" ", "-" ).lower().strip()
	for us in users:
		receiver,full_name=frappe.db.get_value('User', us.user, ['email','full_name'])	
		url=frappe.utils.get_url()
		Email_Subject="""Lab Test Updated For {0}. Ticket no: {1} """.format(lab_test.voucher_no,lab_test.tickect_no)
		pgurl='<a href="'+url+'/app/'+docn+'/'+lab_test.voucher_no+'" >'+lab_test.voucher_no+'</a>'
		#receiver='jayakumar@alantechnologies.net'
		msg=""" Dear {0}<br> 
						Lab Test Request Updated for {1}
						Please click here {2}  Ticket No. {3}  <br> 
						""".format(full_name,lab_test.referance_type,pgurl,lab_test.tickect_no)
		if receiver:
			email_args = {
						"recipients": [receiver],
						"message": msg,
						"subject": Email_Subject,
						"reference_doctype": lab_test.referance_type,
						"reference_name": lab_test.voucher_no
						}
			frappe.enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)

		frappe.msgprint('Notification Email Send to '+full_name)