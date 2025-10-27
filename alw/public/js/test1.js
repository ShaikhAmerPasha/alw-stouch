// frappe.ui.form.on('Imported Sales Invoice', {
//     refresh: function(frm) {
//         frm.add_custom_button(__('Copy to Sales Invoice'), function() {
//             frappe.call({
//                 method: "alw.alw.sales.copy_single_imported_sales_invoice",
//                 args: {
//                     imported_sales_invoice_name: frm.doc.name  // Pass the name of the current Imported Sales Invoice
//                 },
//                 freeze: true,
//                 freeze_message: __('<span style="display: block; text-align: center;">'
//             + '<img src="https://global.discourse-cdn.com/sitepoint/original/3X/e/3/e352b26bbfa8b233050087d6cb32667da3ff809c.gif" alt="Processing" style="width: 100px; height: 100px;"><br>'
//             + 'Please Wait...<br>Connecting to the remote server to retrieve data</span>'),
//                 callback: function(response) {
//                     if (response.message) {
//                         frappe.msgprint(__("Sales Invoice created successfully for the imported invoice: " + frm.doc.name));
//                     }
//                 }
//             });
//         });
//     }
// });
frappe.ui.form.on('Imported Sales Invoice', {
    refresh: function (frm) {
        frm.add_custom_button(__('Copy to Sales Invoice'), function () {
            frappe.call({
                method: "alw.alw.sales.copy_single_imported_sales_invoice",
                args: {
                    imported_sales_invoice_name: frm.doc.name  // Pass the name of the current Imported Sales Invoice
                },
                freeze: true,
                freeze_message: __('<span style="display: block; text-align: center;">'
                    + '<img src="https://global.discourse-cdn.com/sitepoint/original/3X/e/3/e352b26bbfa8b233050087d6cb32667da3ff809c.gif" alt="Processing" style="width: 100px; height: 100px;"><br>'
                    + 'Please Wait...<br>Connecting to the remote server to retrieve data</span>'),
                callback: function (response) {
                    if (response.message.duplicate) {
                        // Show a Yes/No confirmation dialog if duplicate exists
                        frappe.confirm(
                            response.message.message,
                            function () {
                                // User clicked "Yes"
                                frappe.call({
                                    method: "alw.alw.sales.copy_single_imported_sales_invoice",
                                    args: {
                                        imported_sales_invoice_name: frm.doc.name,
                                        force_duplicate: true
                                    },
                                    freeze: true,
                                    freeze_message: __('<span style="display: block; text-align: center;">'
                                        + '<img src="https://global.discourse-cdn.com/sitepoint/original/3X/e/3/e352b26bbfa8b233050087d6cb32667da3ff809c.gif" alt="Processing" style="width: 100px; height: 100px;"><br>'
                                        + 'Please Wait...<br>Copying Sales Invoice</span>'),
                                    callback: function (res) {
                                        frappe.msgprint(res.message.message);
                                    }
                                });
                            },
                            function () {
                                // User clicked "No"
                                frappe.msgprint(__('Operation cancelled.'));
                            }
                        );
                    } else {
                        frappe.msgprint(__("Sales Invoice created successfully for the imported invoice: " + frm.doc.name));
                    }
                }
            });
        });
    }
});

