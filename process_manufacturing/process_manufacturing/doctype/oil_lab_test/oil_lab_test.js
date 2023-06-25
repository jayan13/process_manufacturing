// Copyright (c) 2023, earthians and contributors
// For license information, please see license.txt

frappe.ui.form.on('Oil Lab Test', {
	 //refresh: function(frm) {

		
	 //},
	 density_per_sg: function(frm, cdt, cdn) 
	 { 
		
		 var d = locals[cdt][cdn];
		if(d.density_per_sg && d.net_weight)
		{
			 d.qty_in_litters=Math.round(d.net_weight/d.density_per_sg);
			 frm.refresh_fields();
		 }
	 } ,
	 net_weight: function(frm, cdt, cdn) 
	 { 
		
		 var d = locals[cdt][cdn];
		if(d.density_per_sg && d.net_weight)
		{
			 d.qty_in_litters=Math.round(d.net_weight/d.density_per_sg);
			 frm.refresh_fields();
		 }                
		 
	 } 
});
