frappe.listview_settings['Imported Purchase Invoice'] = {
    onload: function (listview) {
        listview.page.add_button('Import to Purchase Invoice', () => {
            // Define the dialog to select the company
            let dialog = new frappe.ui.Dialog({
                title: 'Select Company',
                fields: [
                    {
                        label: 'Company',
                        fieldname: 'company',
                        fieldtype: 'Link',
                        options: 'Company', // Link to the Company DocType
                        reqd: 1 // Make it mandatory
                    }
                ],
                primary_action_label: 'Submit',
                primary_action: function (data) {
                    if (data.company) {
                        dialog.hide(); // Hide the dialog after submission

                        // Fetch company abbreviation
                        frappe.db.get_value('Company', data.company, 'abbr')
                            .then(response => {
                                const company_abbr = response.message.abbr;

                                if (company_abbr) {
                                    // Call the server-side method with the company abbreviation
                                    frappe.call({
                                        method: "alw.alw.purchase.copy_bulk_imported_invoices_to_purchase",
                                        args: {
                                            company_abbr: company_abbr // Pass company abbreviation
                                        },
                                        freeze: true,
                                        freeze_message: __('<span style="display: block; text-align: center;">'
                                            + '<img src="https://global.discourse-cdn.com/sitepoint/original/3X/e/3/e352b26bbfa8b233050087d6cb32667da3ff809c.gif" alt="Processing" style="width: 100px; height: 100px;"><br>'
                                            + 'Please Wait...<br>Connecting to the remote server to retrieve data</span>'),
                                        callback: function (response) {
                                            if (!response.exc) {
                                                frappe.msgprint(__('Sales invoices copied successfully.'));
                                                listview.refresh(); // Refresh the list view
                                            } else {
                                                frappe.msgprint(__('Failed to copy sales invoices.'));
                                            }
                                        }
                                    });
                                } else {
                                    frappe.msgprint(__('Failed to fetch company abbreviation.'));
                                }
                            });
                    }
                }
            });

            // Show the dialog
            dialog.show();
        });
    }
};
