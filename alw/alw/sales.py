import hashlib
import hmac
import traceback
import requests
from frappe.utils import now
from datetime import datetime, timedelta
import frappe
import random
from frappe.utils import getdate
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file
from frappe import _


@frappe.whitelist(allow_guest=True)
def generate_key(company_abbr):
    """For generate key"""
    # Fetch date_from_string and secret from Complis Site doctype
    company_name = frappe.db.get_value("Company", {"abbr": company_abbr}, "name")
    if not company_name:
        frappe.throw(f"Company with abbreviation {company_abbr} not found.")
    company_doc = frappe.get_doc('Company', company_name)
     # Adjust if specific filters are needed
    date_from_string = company_doc.custom_synced_till
    secret = company_doc.custom_secret_key
    # Convert the date and secret into bytes
    key = date_from_string.encode('utf-8')
    text = secret.encode('utf-8')
    hmac_sha256 = hmac.new(key, text, hashlib.sha256)
    # Generate the hash and convert it to a string in the same format as C#
    hash_code = hmac_sha256.digest()
    calculated_secret = hash_code.hex().upper()  # Convert bytes to uppercase hex string
    return calculated_secret

@frappe.whitelist(allow_guest=True)
def fetch_and_store_imported_sales_invoices(company_abbr="POINT"):
    """for importing sales invoice"""
    # API endpoint and headers

    ### Site_code logic for PGT company.
    company_abbr_PGT = "PGT"
    company_name_PGT = frappe.db.get_value("Company", {"abbr": company_abbr_PGT}, "name")
    custom_account_head_PGT = '2303 - VAT 15% - PGT'
    custom_cost_center_PGT = 'Main - PGT'
    item_income_account = '4110 - Sales - PGT'
    item_expense_account = '5111 - Cost of Goods Sold - PGT'
    isSiteCode=False

    company_name = frappe.db.get_value("Company", {"abbr": company_abbr}, "name")
    if not company_name:
        frappe.throw(f"Company with abbreviation {company_abbr} not found.")
    company_doc = frappe.get_doc('Company', company_name)
    date_from =company_doc.custom_synced_till
    date_to = company_doc.custom_synced_to
    api_key = generate_key(company_abbr)
    url = company_doc.custom_site_url
    headers = {
        "Content-Type": "application/json",
    }
    # Define the payload
    payload = {
        "date_from": date_from,
        "date_to": date_to,
        "key": api_key
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=payload)
    if response is None or not response.text.strip():
        frappe.msgprint("No invoices are available")
    else:

        # Check for a successful request
        if response.status_code == 200:
            data = response.json()
            if data.get('meta', {}).get('success') == "true":
                invoices = data.get('data', [])
                imported_count = 0
                for invoice in invoices:
                    if frappe.db.exists("Imported Sales Invoice", {"invoice_no": invoice.get("invoice_no")}):
                        continue
                    isSiteCode=True if invoice.get("financial_site_code") in ('20') else False    ### Site_code logic for PGT company.
                    doc = frappe.get_doc({
                        "doctype": "Imported Sales Invoice",    
                        ## "custom_company": company_name,    ### Site_code logic for PGT company.
                        "custom_company": company_name_PGT if isSiteCode else company_name,    ### Site_code logic for PGT company.
                        "invoice_no": invoice.get("invoice_no"),
                        "customer_name_en": invoice.get("customer_name_en"),
                        "customer_name_ar": invoice.get("customer_name_ar"),
                        "customer_code": invoice.get("customer_code"),
                        "customer_address_en": invoice.get("customer_address_en"),
                        "customer_address_ar": invoice.get("customer_address_ar"),
                        "customer_building_no_en": invoice.get("customer_building_no_en"),
                        "customer_street_name_en": invoice.get("customer_street_name_en"),
                        "customer_district_en": invoice.get("customer_district_en"),
                        "customer_city_en": invoice.get("customer_city_en"),
                        "customer_country_en": invoice.get("customer_country_en"),
                        "customer_postal_code_en": invoice.get("customer_postal_code_en"),
                        "customer_contact_no_en": invoice.get("customer_contact_no_en"),
                        "customer_building_no_ar": invoice.get("customer_building_no_ar"),
                        "customer_street_name_ar": invoice.get("customer_street_name_ar"),
                        "customer_district_ar": invoice.get("customer_district_ar"),
                        "customer_city_ar": invoice.get("customer_city_ar"),
                        "customer_country_ar": invoice.get("customer_country_ar"),
                        "customer_postal_code_ar": invoice.get("customer_postal_code_ar"),
                        "customer_contact_no_ar": invoice.get("customer_contact_no_ar"),
                        "customer_requestor_en": invoice.get("customer_requestor_en"),
                        "customer_requestor_ar": invoice.get("customer_requestor_ar"),
                        "customer_vat_no": invoice.get("customer_vat_no"),
                        "customer_vendor_code": invoice.get("customer_vendor_code"),
                        "financial_site_code": invoice.get("financial_site_code"),
                        "invoice_date": invoice.get("invoice_date"),
                        "invoice_due_date": invoice.get("invoice_due"),
                        "invoice_account_no": invoice.get("invoice_acc_no"),
                        "agent_name_en": invoice.get("agent_name_en"),
                        "agent_name_ar": invoice.get("agent_name_ar"),
                        "agent_address_en": invoice.get("agent_address_en"),
                        "agent_address_ar": invoice.get("agent_address_ar"),
                        "agent_building_no_en": invoice.get("agent_building_no_en"),
                        "agent_street_name_en": invoice.get("agent_street_name_en"),
                        "agent_district_en": invoice.get("agent_district_en"),
                        "agent_city_en": invoice.get("agent_city_en"),
                        "agent_country_en": invoice.get("agent_country_en"),
                        "agent_postal_code_en": invoice.get("agent_postal_code_en"),
                        "agent_contact_no_en": invoice.get("agent_contact_no_en"),
                        "agent_building_no_ar": invoice.get("agent_building_no_ar"),
                        "agent_street_name_ar": invoice.get("agent_street_name_ar"),
                        "agent_district_ar": invoice.get("agent_district_ar"),
                        "agent_city_ar": invoice.get("agent_city_ar"),
                        "agent_country_ar": invoice.get("agent_country_ar"),
                        "agent_postal_code_ar": invoice.get("agent_postal_code_ar"),
                        "agent_contact_no_ar": invoice.get("agent_contact_no_ar"),
                        "agent_registration_no": invoice.get("agent_registration_no"),
                        "agent_vat_no": invoice.get("agent_vat_no"),
                        "total_excl_tax": invoice.get("total_excl_tax"),
                        "total_tax": invoice.get("total_tax"),
                        "total_incl_tax": invoice.get("total_incl_tax"),
                        "total_local_currency": invoice.get("total_local_currency"),
                        "total_foreign_currency": invoice.get("total_foreign_currency"),
                        "total_excl_tax_fc": invoice.get("total_excl_tax_fc"),
                        "total_tax_fc": invoice.get("total_tax_fc"),
                        "total_incl_tax_fc": invoice.get("total_incl_tax_fc"),
                        "bank_name_en": invoice.get("bank_name_en"),
                        "bank_name_ar": invoice.get("bank_name_ar"),
                        "bank_detail_en": invoice.get("bank_detail_en"),
                        "bank_detail_ar": invoice.get("bank_detail_ar"),
                        "creation": now()
                    })
                    # Save the document
                    doc.insert()
                    # Loop through items and add them to child table
                    duplicate4Check4Prv=""
                    for item in invoice.get("Item_List", []):
                        # duplicate4Check = str(item.get("sr_no"))+item.get("item_desc_en")+str(item.get("item_qty"))+str(item.get("item_tax"))+str(item.get("item_price"))+str(item.get("point_order_no")),
                        duplicate4Check = str(item.get("sr_no"))
                        if (duplicate4Check4Prv!=duplicate4Check): 
                                doc.append("table_pmkf", {
                                    "doctype": "Imported Sales Invoice Item",
                                    "sr_no": item.get("sr_no"),
                                    "item_desc_en": item.get("item_desc_en"),
                                    "item_desc_ar": item.get("item_desc_ar"),
                                    "item_qty": item.get("item_qty"),
                                    "item_tax": item.get("item_tax"),
                                    "item_price": item.get("item_price"),
                                    "point_order_no": item.get("point_order_no"),
                                    "customer_order_no": item.get("customer_order_no"),
                                    "item_version_no": item.get("item_version_no"),
                                    "item_division_en": item.get("item_division_en"),
                                    "item_division_ar": item.get("item_division_ar"),
                                    "item_brand_en": item.get("item_brand_en"),
                                    "item_brand_ar": item.get("item_brand_ar"),
                                    # "income_account": item_income_account if isSiteCode else '',
                                    # "expense_account": item_expense_account if isSiteCode  else '',
                                })
                        duplicate4Check4Prv = item.get("item_desc_en")+str(item.get("item_qty"))+str(item.get("item_tax"))+str(item.get("item_price"))+str(item.get("point_order_no")),

                    doc.append("custom_taxes", {
                        "doctype": "Imported Sales Invoice Taxes",
                        # "account_head": company_doc.custom_sales_account_head,    ### Site_code logic for PGT company.
                        "account_head": custom_account_head_PGT if isSiteCode  else company_doc.custom_sales_account_head,    ### Site_code logic for PGT company.
                        "description": invoice.get("invoice_no"),
                        # "cost_center": company_doc.custom_sales_cost_center,    ### Site_code logic for PGT company.
                        "cost_center": custom_cost_center_PGT if isSiteCode  else company_doc.custom_sales_cost_center,     ### Site_code logic for PGT company.
                        "tax_amount": invoice.get("total_tax"),
                        "total": invoice.get("total_incl_tax")
                    })

                    # Save the document again after adding child items
                    doc.save()
                    imported_count += 1
                frappe.db.commit()
                frappe.msgprint(f"{imported_count} Imported Sales Invoices created successfully!")
            else:
                frappe.throw("Error in fetching data from API: " + data.get('meta', {}).get('message'))
        else:
            frappe.throw("API call failed with status code: " + str(response.status_code))

# fetch_and_store_imported_sales_invoices()
@frappe.whitelist()
def copy_imported_invoices_to_sales_invoices(company_abbr):
    """This function used to copy """
    try:
        time_limit = datetime.now() - timedelta(days=15)    
        old_invoices = frappe.get_all(
                'Imported Sales Invoice', 
                filters={'creation': ('<', time_limit.strftime('%Y-%m-%d %H:%M:%S'))}, 
                pluck='name'
            )
        if old_invoices:
                for invoice_name in old_invoices:
                    frappe.delete_doc('Imported Sales Invoice', invoice_name, force=1, ignore_permissions=True)
                        # frappe.log_error(f"Deleted invoice: {invoice_name}", "Delete Old Invoices")
                    
        # Fetch Complis Site in Company settings
        company_name = frappe.db.get_value("Company", {"abbr": company_abbr}, "name")
        if not company_name:
            frappe.throw(f"Company with abbreviation {company_abbr} not found.")
        company_doc = frappe.get_doc('Company', company_name)
        date_from = company_doc.custom_synced_till
        date_to = company_doc.custom_synced_to
        # Fetch all Imported Sales Invoices within the date range
        imported_invoices = frappe.get_all(
            "Imported Sales Invoice",
            filters={
                "invoice_date": ["between", [date_from, date_to]],
                "is_copied": 0
            },
            fields=["*"]
        )

        skipped_invoices = 0  # Counter for skipped invoices

        for imported_invoice in imported_invoices:
            duplicate_invoice = frappe.db.exists(
                "Sales Invoice",
                {"complis_invoice_number": imported_invoice.invoice_no}
            ) 

            if duplicate_invoice:
                skipped_invoices += 1
                continue
            # Check if the company exists
            company_name = imported_invoice.custom_company
            company = frappe.db.exists("Company", {"name": company_name})

            if not company:
                skipped_invoices += 1
                frappe.msgprint(f"Skipped invoice {imported_invoice.invoice_no}: Company {company_name} does not exist.")
                continue
            company_doc = frappe.get_doc("Company", company)

            # Get or create the customer
            customer_name = imported_invoice.customer_name_en
            existing_customer = frappe.db.exists("Customer", {"customer_name": customer_name})

            if existing_customer:
                customer = frappe.get_doc("Customer", existing_customer)
                if not customer.custom_complis_customer_id:
                    customer.custom_complis_customer_id = imported_invoice.customer_code
                    customer.save(ignore_permissions=True)
                if not customer.tax_id:
                    customer.tax_id = imported_invoice.customer_vat_no
                    customer.save(ignore_permissions=True)
            else:
                new_customer = frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": customer_name,
                    "customer_type": "Company",
                    "customer_group": "Commercial",
                    "territory": "All Territories",
                    "custom_complis_customer_id": imported_invoice.customer_code
                })
                new_customer.insert(ignore_permissions=True)
                customer = new_customer

            # Fetch or create the address
            agent_address = frappe.db.exists("Address", {"address_title": company_name})

            if not agent_address:
                agent_address_doc = frappe.get_doc({
                    "doctype": "Address",
                    "address_title": company_name,
                    "address_type": "Billing",
                    "address_line1": f"{imported_invoice.customer_building_no_en} / {imported_invoice.customer_building_no_ar}",
                    "city": f"{imported_invoice.customer_city_en} / {imported_invoice.customer_city_ar}",
                    "country": imported_invoice.customer_country_en,
                    "custom_country_name_in_arabic": imported_invoice.customer_country_ar,
                    "pincode": imported_invoice.customer_postal_code_en,
                    "links": [{"link_doctype": "Customer", "link_name": customer.name}]
                })
                agent_address_doc.insert(ignore_permissions=True)
                agent_address = agent_address_doc.name

            if not customer.customer_primary_address:
                customer.customer_primary_address = agent_address
                customer.save(ignore_permissions=True)

            # Retrieve the default income account
            income_account = frappe.db.get_value(
                "Account",
                {"company": company_doc.name, "root_type": "Income", "is_group": 0},
                "name"
            )
            if not income_account:
                frappe.throw(f"No default income account found for the company {company_doc.name}.")

            # Determine if the invoice should be a Credit Note
            is_credit_note = (
                float(imported_invoice.total_excl_tax or 0) < 0 or
                float(imported_invoice.total_tax or 0) < 0 or
                float(imported_invoice.total_incl_tax or 0) < 0
            )

            # Create a new Sales Invoice or Credit Note
            new_sales_invoice = frappe.new_doc("Sales Invoice")
            new_sales_invoice.is_return = 1 if is_credit_note else 0  # Mark as Credit Note if needed
            if new_sales_invoice.is_return != 1:
                new_sales_invoice.naming_series = company_doc.custom_sales_invoice_series
            else :
                new_sales_invoice.naming_series = company_doc.custom_sales_return_series

            # Map fields from Imported Sales Invoice to Sales Invoice
            new_sales_invoice.customer = customer.name
            new_sales_invoice.complis_invoice_number = imported_invoice.invoice_no
            new_sales_invoice.customer_name_in_arabic = imported_invoice.customer_name_en
            new_sales_invoice.custom_customer_name_in_arabic = imported_invoice.customer_name_ar
            new_sales_invoice.posting_date = imported_invoice.invoice_date
            new_sales_invoice.due_date = imported_invoice.invoice_due_date
            new_sales_invoice.total = abs(float(imported_invoice.total_excl_tax or 0))
            new_sales_invoice.total_taxes_and_charges = abs(float(imported_invoice.total_tax or 0))
            new_sales_invoice.grand_total = abs(float(imported_invoice.total_incl_tax or 0))
            new_sales_invoice.company = company_doc.name
            new_sales_invoice.currency = company_doc.default_currency
            new_sales_invoice.taxes_and_charges = company_doc.custom_sales_tax_template
            new_sales_invoice.total_foreign_currency = imported_invoice.total_foreign_currency
            new_sales_invoice.total_excl_tax = imported_invoice.total_excl_tax_fc
            new_sales_invoice.total_tax = imported_invoice.total_tax_fc
            new_sales_invoice.total_incl_tax = imported_invoice.total_incl_tax_fc

            # Add items to the Sales Invoice
            imported_items = frappe.get_all(
                "Imported Sales Invoice Item",
                filters={"parent": imported_invoice.get("name")},
                fields=["*"]
            )

            for imported_item in imported_items:
                item_code = ensure_item_exists(imported_item.item_desc_en)
                new_sales_invoice.append("items", {
                    "item_name": imported_item.item_desc_en,
                    "item_code" :item_code,
                    "qty": float(imported_item.item_qty or 0),  # Use absolute qty for consistency
                    # "rate": abs(float(imported_item.item_price or 0)),
                    "rate": (abs(float(imported_item.item_price or 0)/imported_item.item_qty)),
                    "amount": (float(imported_item.item_tax or 0)),  # Use absolute amount
                    "income_account": company_doc.custom_receivable_account,
                    "complis_item_no": imported_item.sr_no,
                    "custom_complis_item_no": imported_item.sr_no,
                    "purchase_order_no": imported_item.customer_order_no,
                    # "pos_invoice": imported_item.point_order_no,

                })

            # Fetch custom taxes for this invoice
            custom_taxes = frappe.get_all(
                "Imported Sales Invoice Taxes",
                filters={"parent": imported_invoice.get("name")},
                fields=["*"]
            )

            # Add custom taxes to the Sales Invoice
            for custom_tax in custom_taxes:
                new_sales_invoice.append("taxes", {
                    "charge_type": "On Net Total",
                    "account_head": company_doc.custom_sales_account_head,
                    "description": imported_invoice.invoice_no,
                    "cost_center": company_doc.custom_sales_cost_center,
                    "rate": 15,
                    "tax_amount": (float(imported_invoice.total_tax or 0)),
                    "total": (float(imported_invoice.total_incl_tax or 0))
                })

            # Insert the new Sales Invoice into the database
            new_sales_invoice.insert()

            # Mark the Imported Sales Invoice as copied
            frappe.db.set_value("Imported Sales Invoice", imported_invoice.get("name"), "is_copied", 1)
        frappe.db.commit()
        frappe.msgprint(f"{len(imported_invoices) - skipped_invoices} Sales Invoices created successfully! ")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in copy_imported_invoices_to_sales_invoices")
        frappe.throw(f"An error occurred: {str(e)}")

@frappe.whitelist(allow_guest=True)
def copy_single_imported_sales_invoice(imported_sales_invoice_name,force_duplicate=False):
    """Function for bulk operation"""
    try:
        # Fetch the specified Imported Sales Invoice
        imported_invoice = frappe.get_doc("Imported Sales Invoice", imported_sales_invoice_name)
        # doc_name = frappe.get_all("Complis Site", fields=["name"], limit=1)

        # if doc_name:
        #     import_settings = frappe.get_doc("Complis Site", doc_name[0].name)
        # else:
        #     frappe.throw("No Complis Site document found.")
        # Check if it has already been copied
        duplicate_invoice = frappe.db.exists(
            "Sales Invoice",
            {
                "complis_invoice_number": imported_invoice.invoice_no
            }
        )
        if duplicate_invoice and not force_duplicate:
            return {
                "duplicate": True,
                "message": f"Invoice {imported_invoice.invoice_no} already exists. Do you want to copy it again?"
            }

    
        if imported_invoice.is_copied:
            frappe.throw(f"The invoice {imported_sales_invoice_name} has already been copied to a Sales Invoice.")

        # Fetch or create the company linked to agent_name_en
        company_name = imported_invoice.custom_company
        company = frappe.db.exists("Company", {"name": company_name})
        if not company:
            # Create a new Company if it doesn't exist
            frappe.throw(f"Cannot copy Imported Sales Invoice {imported_invoice} because the company  does not exist.")

        # Load the company document for further use
        company_doc = frappe.get_doc("Company", company)

        # Get or create the customer based on customer_name_en
        customer_name = imported_invoice.customer_name_en
        existing_customer = frappe.db.exists("Customer", {"customer_name": customer_name})

        if existing_customer:
            # Use existing customer and update missing fields if necessary
            customer = frappe.get_doc("Customer", existing_customer)
            if not customer.custom_complis_customer_id:
                customer.custom_complis_customer_id = imported_invoice.customer_code
                customer.save(ignore_permissions=True)
            if not customer.tax_id:
                customer.tax_id = imported_invoice.customer_vat_no
                customer.save(ignore_permissions=True)
        else:
            # Create a new customer if it doesn't exist
            new_customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_name,
                "customer_type": "Company",
                "customer_group": "Commercial",
                "territory": "All Territories",
                "custom_complis_customer_id": imported_invoice.customer_code
            })
            new_customer.insert(ignore_permissions=True)
            customer = new_customer

        # Fetch or create the agent's address
        agent_address = frappe.db.exists("Address", {"address_title": company_name})

        if not agent_address:
            # Create a new address if it doesn't exist
            agent_address_doc = frappe.get_doc({
                "doctype": "Address",
                "address_title": company_name,
                "address_type": "Billing",
                "address_line1": f"{imported_invoice.customer_building_no_en} / {imported_invoice.customer_building_no_ar}",
                "city": f"{imported_invoice.customer_city_en} / {imported_invoice.customer_city_ar}",
                "country": imported_invoice.customer_country_en,
                "custom_country_name_in_arabic": imported_invoice.customer_country_ar,
                "pincode": imported_invoice.customer_postal_code_en,
                "links": [{"link_doctype": "Customer", "link_name": customer.name}]
            })
            agent_address_doc.insert(ignore_permissions=True)
            agent_address = agent_address_doc.name

        # Update the customer's primary address if not already set
        if not customer.customer_primary_address:
            customer.customer_primary_address = agent_address
            customer.save(ignore_permissions=True)

        # Retrieve the default income account for the company
        income_account = frappe.db.get_value(
            "Account", 
            {"company": company_doc.name, "root_type": "Income", "is_group": 0}, 
            "name"
        )
        if not income_account:
            frappe.throw(f"No default income account found for the company {company_doc.name}.")

        # Determine if the invoice should be a Credit Note
        is_credit_note = (
            float(imported_invoice.total_excl_tax or 0) < 0 or
            float(imported_invoice.total_tax or 0) < 0 or
            float(imported_invoice.total_incl_tax or 0) < 0
        )

        # Create a new Sales Invoice or Credit Note
        new_sales_invoice = frappe.new_doc("Sales Invoice")
        new_sales_invoice.is_return = 1 if is_credit_note else 0 
        if new_sales_invoice.is_return != 1:
            new_sales_invoice.naming_series = company_doc.custom_sales_invoice_series
        else :
            new_sales_invoice.naming_series = company_doc.custom_sales_return_series


        # Map fields from Imported Sales Invoice to Sales Invoice
        new_sales_invoice.customer = customer.name
        new_sales_invoice.custom_customer_name_in_arabic = imported_invoice.customer_name_ar
        new_sales_invoice.customer_name_in_arabic = imported_invoice.customer_name_en
        new_sales_invoice.complis_invoice_number = imported_invoice.invoice_no
        new_sales_invoice.posting_date = imported_invoice.invoice_date
        new_sales_invoice.due_date = imported_invoice.invoice_due_date
        new_sales_invoice.total = abs(float(imported_invoice.total_excl_tax or 0))
        new_sales_invoice.total_taxes_and_charges = abs(float(imported_invoice.total_tax or 0))
        new_sales_invoice.grand_total = abs(float(imported_invoice.total_incl_tax or 0))
        new_sales_invoice.company = company_doc.name
        new_sales_invoice.currency = company_doc.default_currency
        new_sales_invoice.taxes_and_charges=company_doc.custom_sales_tax_template
        new_sales_invoice.total_foreign_currency= imported_invoice.total_foreign_currency
        new_sales_invoice.total_excl_tax = imported_invoice.total_excl_tax_fc
        new_sales_invoice.total_tax = imported_invoice.total_tax_fc
        new_sales_invoice.total_incl_tax = imported_invoice.total_incl_tax_fc
        # Process item list from the Imported Sales Invoice
        for imported_item in imported_invoice.table_pmkf:
            item_code = ensure_item_exists(imported_item.item_desc_en)
            new_sales_invoice.append("items", {
                "item_name": imported_item.item_desc_en,
                "item_code" :item_code,
                "qty": imported_item.item_qty or 0,
                "rate": abs(float(imported_item.item_price or 0)/imported_item.item_qty),
                "amount": float(imported_item.item_tax or 0),
                "income_account": company_doc.custom_receivable_account,
                "complis_item_no": imported_item.sr_no,
                "custom_complis_item_no": imported_item.sr_no,
                "purchase_order_no": imported_item.customer_order_no,
                # "pos_invoice": imported_item.point_order_no,

            })
        for custom_tax in imported_invoice.custom_taxes:
            new_sales_invoice.append("taxes", {
            "doctype": "Sales Taxes and Charges",
            "charge_type": "On Net Total",  # Adjust based on your requirement
            "account_head": company_doc.custom_sales_account_head,
            "description": imported_invoice.invoice_no,
            "cost_center": company_doc.custom_sales_cost_center ,
            "rate": 15,  # Assuming rate is 0 as per your initial data; adjust if necessary
            "tax_amount": (float(imported_invoice.total_tax or 0)),
            "total": (float(imported_invoice.total_incl_tax or 0))
        })
        # Insert the new Sales Invoice or Credit Not         e into the database
        new_sales_invoice.insert()
        frappe.db.commit()

        # Mark the Imported Sales Invoice as copied
        imported_invoice.is_copied = 1
        imported_invoice.save()
        frappe.db.commit()

        frappe.msgprint(f"Sales Invoice {new_sales_invoice.name} created successfully for Imported Sales Invoice {imported_invoice.name}!")

    except Exception as e:
        frappe.log_error(message=str(e), title="Error copying Imported Sales Invoice")
        frappe.throw(f"An error occurred while creating Sales Invoice: {str(e)}")

def ensure_item_exists(item_name):
    """Ensure the item exists in the Item doctype; if not, create it."""

    try:
        existing_item = frappe.db.get_value("Item", {"item_name": item_name, "is_stock_item": 0}, "item_code")
        # frappe.throw(existing_item)
        if existing_item:
            return existing_item

        # elsif not frappe.db.exists("Item", {"item_name": item_name} ):
        else:
            new_item = frappe.get_doc({
                "doctype": "Item",
                "item_name": item_name,
                "item_group": "Services",
                "is_stock_item": 0,
                # "naming_series": "STO-ITEM-.{#####}",
                "item_code": str(random.randint(1000000000, 9999999999))
            })
            new_item.insert(ignore_permissions=True)
            frappe.db.commit()
            return new_item.item_code
    except Exception as e:
        frappe.throw(str(e)+" ITEM: "+item_name)


##############################################################
###-START=> TO SCHEDULE THE SYNC SALES JOB WRITTEN BY HASEEB
##############################################################
from alw.alw.helpers import get_current_date_iso
def schedule_sales_import():
    company_abbr="POINT"
    try:
        got_company_name = frappe.db.get_value("Company", {"abbr": company_abbr}, "name")
        if not got_company_name: ## RECORD NOT FOUND
            #print("Not Found")
            return None
        else: ## RECORD FOUND
            #print("Found: ", got_company_name)
            # Set the value of the "Sync Dates" field for the Cpmplis Integration into Company Doctype.
            company_doc = frappe.get_doc("Company", got_company_name)
            company_doc.custom_synced_till =  get_current_date_iso(5, "00:00:01")
            company_doc.custom_synced_to = get_current_date_iso(0, "23:59:59")
            company_doc.save()  ##Save the changes
            frappe.db.commit()  ##Commit the transaction

            fetch_and_store_imported_sales_invoices(company_abbr) ##Fetching Invoices
            copy_imported_invoices_to_sales_invoices(company_abbr) ##POSTING IMPORTED INVOICE INTO INVOICE DOCTYPE

            return got_company_name
    except Exception as e:
        frappe.throw(str(e) + " COMPANY: " + company_abbr)
##############################################################
###-END=> TO SCHEDULE THE SYNC SALES JOB WRITTEN BY HASEEB
##############################################################




##############################################################
###-START=> API FOR SALES INVOICES WRITTEN BY HASEEB
    # API Calls:  
        # bench execute alw.alw.sales.siapi --kwargs '{"date_from":"2025-01-01","date_to":"2025-01-20"}'
        # curl -X POST   https://erp.tzamun.sa/api/method/alw.alw.sales.siapi   -H "Content-Type: application/json"   -d '{"date_from":"2025-01-01", "date_to":"2025-01-20"}'
        # curl -X POST   https://erp.tzamun.sa/api/method/alw.alw.sales.siapi   -H "Content-Type: application/json"   -H "Authorization: token <api-key>:<api-secret>"   -d '{"date_from":"2025-01-01", "date_to":"2025-01-20"}'
    # Returns a list of Sales Invoices between DateFrom and DateTo.
    # :param date_from: Start date (YYYY-MM-DD)
    # :param date_to: End date (YYYY-MM-DD)
    # :return: List of Sales Invoices
##############################################################
import frappe
from frappe.utils import getdate
from frappe.core.doctype.file.file import get_url


@frappe.whitelist(allow_guest=True)
def siapi(key,date_from,date_to):

    # company_abbr="PGT" ##POINT
    # company_name, default_letter_head, custom_default_print_format_for_sales_invoice = frappe.db.get_value(
    #     "Company", {"abbr": company_abbr}, ["name", "default_letter_head","custom_default_print_format_for_sales_invoice"]
    # )

    company_abbrs = ["PGT", "POINT"]
    companies = frappe.get_all(
        "Company",
        filters={"abbr": ["in", company_abbrs]},
        fields=["abbr", "name"]
    )
    company_name = [c["name"] for c in companies]

    # company_abbrs = ["PGT", "POINT"]
    # companies = frappe.get_all(
    #     "Company",
    #     filters={"abbr": ["in", company_abbrs]},
    #     fields=["abbr", "name", "default_letter_head", "custom_default_print_format_for_sales_invoice"]
    # )
    # company_map = {c["abbr"]: c for c in companies}

    
    date_from = getdate(date_from)
    date_to = getdate(date_to)
    # date_from = getdate('2025-01-01')
    # date_to = getdate('2025-01-31')
    base_url = frappe.utils.get_url()


    try:

        # # Check if the duration exceeds 10 days
        # if (date_to - date_from).days > 10:
        #     return {
        #         "code": "400",
        #         "status": "error",
        #         "message": "The date range cannot exceed 10 days. Please select a shorter duration."
        #     }


        api = frappe.get_attr("alw.alw.apikey.validate_key_siapi")
        response = api(key)
        if response.get("valid") == "0":
            return {"status": "error", "message": "Invalid API key validation"}
        else:
            invoices = frappe.get_all(
                "Sales Invoice",
                filters={
                    "posting_date": ["between", [date_from, date_to]],
                    "status": ["in", ["Paid", "Unpaid","Submitted"]],
                    "company": ["in", company_name],  # Fetch only selected companies
                    # "company": company_name  # Fetch only selected company
                },
                fields=["company","name","complis_invoice_number", "status","custom_zatca_status","customer", "customer_name","posting_date", "total","total_taxes_and_charges","grand_total","currency"]
            )
            if not invoices: ## RECORD NOT FOUND
                return {"code":"210","status": "Success", "message": "Record Not Found"}
            else: ## RECORD FOUND
                # Iterate through the invoices and set null values to empty string
                for invoice in invoices:
                    
                    default_letter_head, custom_default_print_format_for_sales_invoice = frappe.db.get_value(
                        "Company", {"name": invoice['company']}, ["default_letter_head","custom_default_print_format_for_sales_invoice"]
                    )
                    invoice["debuger"] = "none"

                    # Generate PDF file name
                    file_name = f"Sales_Report_{invoice['name']}.pdf"
                    invoice["debuger"] = f"{file_name}"


                    ### Delete the file if it already exists
                    # existing_file = frappe.db.get_value("File", {"file_name": file_name}, ["name"])
                    # if existing_file:
                    #     frappe.delete_doc("File", existing_file, ignore_permissions=True)


                    # Check if the file already exists
                    existing_file = frappe.db.get_value("File", {"file_name": file_name}, ["file_url"])
                    if existing_file:
                        # Use existing file URL
                        file_url = f"{base_url}{existing_file}"
                    else:
                        # Save letterhead temporarily
                        frappe.db.set_value("Sales Invoice", invoice["name"], "letter_head", default_letter_head)
                        # # Fetch the document with ignore_permissions=True
                        invoice_doc = frappe.get_doc("Sales Invoice", invoice["name"], ignore_permissions=True)
                        invoice_doc.letter_head = "PG Letterhead"
                        invoice_doc.flags.ignore_permissions = True
                        invoice_doc.flags.ignore_mandatory = True  # Ignore mandatory fields if necessary
                        invoice_doc.check_permission = lambda *args, **kwargs: True
                        invoice_doc.run_method("load_doc_before_save")  # Helps bypass certain validation checks

                        # Generate the PDF report using the specified print format
                        # frappe.local.form_dict.letterhead = "PG Letterhead"
                        frappe.local.session.user = "Administrator"  # Temporarily switch user

                        report_html = frappe.get_print("Sales Invoice", invoice_doc.name, print_format=custom_default_print_format_for_sales_invoice)
                        # Convert the HTML to a PDF file
                        pdf_data = get_pdf(report_html)


                        # Save the file **without attaching it to Sales Invoice**
                        file_doc = frappe.get_doc({
                            "doctype": "File",
                            "file_name": file_name,
                            "content": pdf_data,
                            "is_private": 0  # Make it public
                        })
                        file_doc.save(ignore_permissions=True)

                        # Get the public URL of the saved file
                        file_url = file_doc.file_url

                        # Ensure the file URL is absolute
                        if not file_url.startswith(("http://", "https://")):
                            file_url = f"{base_url}{file_url}"

                    # Add the generated PDF file URL to the invoice dictionary
                    invoice["pdf_report_url"] = file_url



                    # Fetch all attachments for the current invoice
                    base_url = frappe.utils.get_url()
                    attachments =[
                        attachment for attachment in frappe.get_all(
                            "File",
                            filters={
                                "attached_to_doctype": "Sales Invoice",
                                "attached_to_name": invoice["name"],
                            },
                            fields=["name","file_name", "file_url","is_private"]
                        ) if not any(keyword.lower() in attachment["file_name"].lower() for keyword in [".xml","Cleared xml","QR_image"])
                    ]

                   # Ensure the file_url is absolute
                    for attachment in attachments:
                        file_url = attachment['file_url']  # Make sure to start with the current file_url

                        # # Check if the file name contains unwanted substrings
                        # if any(keyword.lower() in attachment["file_name"].lower()  for keyword in ["xml", "QR_image"]):
                        #     continue  # Skip adding this attachment
                        
                        # Update the File doctype if the file is private
                        # if attachment.get("is_private", 0) == 1:
                        #     file_doc = frappe.get_doc("File", attachment["name"])
                            # file_doc.is_private = 0  # Set to public
                            # file_doc.save(ignore_permissions=True)
                            # frappe.db.commit()
                            # file_url = attachment['file_url'].replace("/private/files/", "/files/")  # Update the path to public folder

                        # if attachment.get("is_private", 0) == 1:
                        #     file_url = get_url(attachment["name"])  # Generate an accessible URL

                        # Ensure the file_url is absolute
                        if not file_url.startswith(("http://", "https://")):
                            attachment["file_url"] = f"{base_url}{file_url}"
                        else:
                            # If it's already an absolute URL, just update the attachment file_url
                            attachment["file_url"] = file_url

                    # Add the attachments to the invoice dictionary
                    invoice["attachments"] = attachments

                return {"code":"200","status": "success", "data": invoices}

    except Exception as e:
        # Get the full traceback of the error
        error_message = str(e)
        error_trace = traceback.format_exc()  # To capture the full stack trace

        # Log the full error details
        frappe.log_error(error_trace, "siapi - Error generating PDF report")

        # Return a more informative error response
        return {
            "code": "400",
            "status": "error",
            "message": "An error occurred while processing your request.",
            "details": {
                "error_message": error_message,
                "traceback": error_trace
            }
        }
##############################################################
###-END=> API FOR SALES INVOICES WRITTEN BY HASEEB
##############################################################



# ##############################################################
# ###-START=> API FOR SALES INVOICES WRITTEN BY HASEEB
#     # API Calls:  
#         # bench execute alw.alw.sales.siapi --kwargs '{"date_from":"2025-01-01","date_to":"2025-01-20"}'
#         # curl -X POST   https://erp.tzamun.sa/api/method/alw.alw.sales.siapi   -H "Content-Type: application/json"   -d '{"date_from":"2025-01-01", "date_to":"2025-01-20"}'
#         # curl -X POST   https://erp.tzamun.sa/api/method/alw.alw.sales.siapi   -H "Content-Type: application/json"   -H "Authorization: token <api-key>:<api-secret>"   -d '{"date_from":"2025-01-01", "date_to":"2025-01-20"}'
#     # Returns a list of Sales Invoices between DateFrom and DateTo.
#     # :param date_from: Start date (YYYY-MM-DD)
#     # :param date_to: End date (YYYY-MM-DD)
#     # :return: List of Sales Invoices
# ##############################################################
# import frappe
# from frappe.utils import getdate
# @frappe.whitelist(allow_guest=True)
# def siapi(key,date_from,date_to):
#     company_abbr="POINT"
#     company_name = frappe.db.get_value("Company", {"abbr": company_abbr}, "name")
#     date_from = getdate(date_from)
#     date_to = getdate(date_to)
#     date_from = getdate('2023-12-01')
#     date_to = getdate('2025-01-31')
#     try:
#         api = frappe.get_attr("alw.alw.apikey.validate_key_siapi")
#         response = api(key)
#         if response.get("valid") == "0":
#             return {"status": "error", "message": "Invalid API key validation"}
#         else:
#             invoices = frappe.get_all(
#                 "Sales Invoice",
#                 filters={
#                     "posting_date": ["between", [date_from, date_to]],
#                     "status": ["in", ["Paid", "Submitted"]],
#                     "company": company_name  # Fetch only selected company
#                 },
#                 fields=["name", "status","custom_zatca_status","customer", "customer_name","posting_date", "total","total_taxes_and_charges","grand_total","currency"]
#             )
#             if not invoices: ## RECORD NOT FOUND
#                 return {"code":"210","status": "Success", "message": "Record Not Found"}
#             else: ## RECORD FOUND
#                 # Iterate through the invoices and set null values to empty string
#                 # for invoice in invoices:
#                 #     if invoice.get('custom_complis_ptdrive_no') is None: invoice['custom_complis_ptdrive_no'] = ''
#                 #     if invoice.get('custom_complis_company_code') is None: invoice['custom_complis_company_code'] = ''
#                 return {"code":"200","status": "success", "data": invoices}

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "siapi")
#         return {"code":"400","status": "error", "message": str(e)}
# ##############################################################
# ###-END=> API FOR SALE INVOICES WRITTEN BY HASEEB
# ##############################################################