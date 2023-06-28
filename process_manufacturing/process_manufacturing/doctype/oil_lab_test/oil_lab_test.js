// Copyright (c) 2023, earthians and contributors
// For license information, please see license.txt

frappe.ui.form.on('Oil Lab Test', {
	 refresh: function(frm) {
		frm.set_query("voucher_no", function () {
			return {
				filters: {"company": 'Dure Oil Middle East Factory - Sole Proprietorship LLC'}
			}
		});
		
	 } 
});
