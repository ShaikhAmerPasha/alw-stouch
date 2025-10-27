

// frappe.ui.form.on("Complis Site", {
//     refresh(frm) {
//         // Refresh logic if any
//     },
//     sync_invoices: function(frm) {
//         frappe.call({
//             method: "alw.alw.sales.fetch_and_store_imported_sales_invoices",
//             args: {
//                 import_invoice: frm.doc.name
//             },
//             callback: function(r) {
//                 if (!r.exc) {
//                     frappe.msgprint(__('Sales invoices imported successfully.'));
//                     frm.save();
//                 } else {
//                     frappe.msgprint(__('Failed to import sales invoices.'));
//                 }
//             }
//         });
//     },
//     custom_import_to_sales_invoice: function(frm) {
//         frappe.call({
//             method: "alw.alw.sales.copy_imported_invoices_to_sales_invoices",
//             args: {
//                 import_invoice: frm.doc.name
//             },
//             callback: function(r) {
//                 if (!r.exc) {
//                     frappe.msgprint(__('Sales invoices copied successfully.'));
//                     frm.save();
//                 } else {
//                     frappe.msgprint(__('Failed to copy sales invoices.'));
//                 }
//             }
//         });
//     }
// });
frappe.ui.form.on("Company", {
    refresh(frm) {
        // Add the new button for bulk purchase invoice import
        frm.add_custom_button(__('Import to Purchase Invoice'), function() {
            frm.trigger('custom_import_to_purchase_invoice');
        });
    },

    custom_sync_invoices: function(frm) {
        frappe.call({
            method: "alw.alw.sales.fetch_and_store_imported_sales_invoices",
            args: {
                company_abbr: frm.doc.abbr
            },
            freeze: true,
            freeze_message: __('<span style="display: block; text-align: center;">'
            + '<img src="https://global.discourse-cdn.com/sitepoint/original/3X/e/3/e352b26bbfa8b233050087d6cb32667da3ff809c.gif" alt="Processing" style="width: 100px; height: 100px;"><br>'
            + 'Please Wait...<br>Connecting to the remote server to retrieve data</span>'),
            callback: function(r) {
                if (!r.exc) {
                    frappe.msgprint(__('Sales invoices imported successfully.'));
                    frm.save();
                } else {
                    frappe.msgprint(__('Failed to import sales invoices.'));
                }
                
            }
        });

    },

    custom_import_to_sales_invoice: function(frm) {
        frappe.call({
            method: "alw.alw.sales.copy_imported_invoices_to_sales_invoices",
            args: {
                company_abbr: frm.doc.abbr,
            },
            freeze: true,
            freeze_message: __('<span style="display: block; text-align: center;">'
            + '<img src="https://global.discourse-cdn.com/sitepoint/original/3X/e/3/e352b26bbfa8b233050087d6cb32667da3ff809c.gif" alt="Processing" style="width: 100px; height: 100px;"><br>'
            + 'Please Wait...<br>Connecting to the remote server to retrieve data</span>'),
            callback: function(r) {
                if (!r.exc) {
                    frappe.msgprint(__('Sales invoices copied successfully.'));
                    frm.save();
                } else {
                    frappe.msgprint(__('Failed to copy sales invoices.'));
                }
            }
        });
    },

    custom_sync_purchase_invoices: function(frm) {
        frappe.call({
            method: "alw.alw.purchase.fetch_and_store_imported_purchase_invoices",
            args: {
                company_abbr: frm.doc.abbr
            },
            freeze: true,
            freeze_message: __('<span style="display: block; text-align: center;">'
            + '<img src="https://global.discourse-cdn.com/sitepoint/original/3X/e/3/e352b26bbfa8b233050087d6cb32667da3ff809c.gif" alt="Processing" style="width: 100px; height: 100px;"><br>'
            + 'Please Wait...<br>Connecting to the remote server to retrieve data</span>'),
            callback: function(r) {
                if (!r.exc) {
                    frappe.msgprint(__('Purchase invoices imported successfully.'));
                    frm.save();
                } else {
                    frappe.msgprint(__('Failed to import purchase invoices.'));
                }
            }
        });
    },

    custom_import_to_purchase_invoice: function(frm) {
        frappe.call({
            method: "alw.alw.purchase.copy_bulk_imported_invoices_to_purchase",
            args: {
                company_abbr: frm.doc.abbr
            },
            freeze: true,
            freeze_message: __('<span style="display: block; text-align: center;">'
            + '<img src="https://global.discourse-cdn.com/sitepoint/original/3X/e/3/e352b26bbfa8b233050087d6cb32667da3ff809c.gif" alt="Processing" style="width: 100px; height: 100px;"><br>'
            + 'Please Wait...<br>Connecting to the remote server to retrieve data</span>'),
            callback: function(r) {
                if (!r.exc) {
                    frappe.msgprint(__('Purchase invoices copied successfully.'));
                    frm.save();
                } else {
                    frappe.msgprint(__('Failed to copy purchase invoices.'));
                }
            }
        });
    }
});
