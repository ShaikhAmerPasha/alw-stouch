// frappe.ui.form.on('Imported Purchase Invoice', {
//     refresh: function(frm) {
//         frm.add_custom_button(__('Copy to Purchase Invoice'), function() {
//             frappe.call({
//                 method: "alw.alw.purchase.copy_single_imported_invoice_to_purchase",
//                 args: {
//                     invoice_name: frm.doc.name  // Pass the name of the current Imported Sales Invoice
//                 },
//                 freeze: true,
//                 freeze_message: __('<span style="display: block; text-align: center;">'
//             + '<img src="https://global.discourse-cdn.com/sitepoint/original/3X/e/3/e352b26bbfa8b233050087d6cb32667da3ff809c.gif" alt="Processing" style="width: 100px; height: 100px;"><br>'
//             + 'Please Wait...<br>Connecting to the remote server to retrieve data</span>'),
//                 callback: function(response) {
//                     if (response.message) {
//                         frappe.msgprint(__("PurchaseInvoice created successfully for the imported invoice: " + frm.doc.name));
//                     }
//                 }
//             });
//         });
//     }
// });
frappe.ui.form.on('Imported Purchase Invoice', {
    refresh: function (frm) {
        frm.add_custom_button(__('Copy to Purchase Invoice'), function () {
            frappe.call({
                method: "alw.alw.purchase.copy_single_imported_invoice_to_purchase",
                args: {
                    invoice_name: frm.doc.name  // Pass the name of the current Imported Purchase Invoice
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
                                // If "Yes", call the function again with force_duplicate=True
                                frappe.call({
                                    method: "alw.alw.purchase.copy_single_imported_invoice_to_purchase",
                                    args: {
                                        invoice_name: frm.doc.name,
                                        force_duplicate: true
                                    },
                                    freeze: true,
                                    freeze_message: __('<span style="display: block; text-align: center;">'
                                        + '<img src="https://global.discourse-cdn.com/sitepoint/original/3X/e/3/e352b26bbfa8b233050087d6cb32667da3ff809c.gif" alt="Processing" style="width: 100px; height: 100px;"><br>'
                                        + 'Please Wait...<br>Copying Purchase Invoice</span>'),
                                    callback: function (res) {
                                        frappe.msgprint(res.message.message);
                                    }
                                });
                            },
                            function () {
                                // If "No", show a cancellation message
                                frappe.msgprint(__('Operation cancelled.'));
                            }
                        );
                    } else {
                        frappe.msgprint(__("Purchase Invoice created successfully for the imported invoice: " + frm.doc.name));
                    }
                }
            });
        });
    }
});
