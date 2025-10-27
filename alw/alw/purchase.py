from io import BytesIO
from datetime import date, datetime, timedelta
import frappe
import requests
from frappe.utils import now
from frappe import _


@frappe.whitelist(allow_guest=True)
def fetch_and_store_imported_purchase_invoices(company_abbr):
    """for import invoices"""

    # API endpoint and headers
    company_name = frappe.db.get_value("Company", {"abbr": company_abbr}, "name")
    if not company_name:
        frappe.throw(f"Company with abbreviation {company_abbr} not found.")
    company_doc = frappe.get_doc('Company', company_name)
    date_from = company_doc.custom_sync_start
    date_to = company_doc.custom_sync_end
    api_key = company_doc.custom_secret_keys
    url = company_doc.custom_site_urls
    headers = {
        "Content-Type": "application/json",
    }


    ### Site_code logic for PGT company.
    company_abbr_PGT = "PGT"
    company_name_PGT = frappe.db.get_value("Company", {"abbr": company_abbr_PGT}, "name")
    company_doc_PGT = frappe.get_doc('Company', company_name_PGT)
    # custom_account_head_PGT = '2303 - VAT 15% - PGT'
    # custom_cost_center_PGT = 'Main - PGT'
    # item_income_account = '4110 - Sales - PGT'
    # item_expense_account = '5111 - Cost of Goods Sold - PGT'
    isSiteCode=False



    # Define the payload
    payload = {
        "date_from": date_from,
        "date_to": date_to,
        "Secret": api_key
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
                    # frappe.msgprint(invoice.get("invoice_no"))
                    if not invoice.get("attachments") or not any(attachment.get("download_link") for attachment in invoice.get("attachments")): 
                        continue
                    # if frappe.db.exists("Imported Purchase Invoice", {"invoice_no": invoice.get("invoice_no")}):
                    #     continue
                    if frappe.db.exists("Imported Purchase Invoice", {
                                "invoice_no": invoice.get("invoice_no"), #Haseeb's Changed On 21-12-2024
                                # "bill_no": invoice.get("invoice_no"), #Haseeb's Changed On 21-12-2024
                                "supplier_code": invoice.get("supplier_code")
                            }):
                        continue
                    isSiteCode=True if invoice.get("financial_site_code") in ('20') else False    ### Site_code logic for PGT company.
                    doc = frappe.get_doc({
                        "doctype": "Imported Purchase Invoice",
                        ## "custom_company": company_name,    ### Site_code logic for PGT company.
                        "custom_company": company_name_PGT if isSiteCode else company_name,    ### Site_code logic for PGT company.
                        "supplier_name_en": invoice.get("supplier_name_en"),
                        "supplier_name_ar": invoice.get("supplier_name_ar"),
                        "supplier_code": invoice.get("supplier_code"),
                        "supplier_address_en": invoice.get("supplier_address_en"),
                        "supplier_address_ar": invoice.get("supplier_address_ar"),
                        "supplier_vat_no": invoice.get("supplier_vat_no"),
                        "invoice_no": invoice.get("invoice_no"),
                        # "bill_no": invoice.get("invoice_no"), #Haseeb's Changed On 21-12-2024
                        "invoice_date": invoice.get("invoice_date"),
                        "invoice_due" : invoice.get("invoice_due"),
                        "invoice_account_no": invoice.get("invoice_acc_no"),
                        "is_return": invoice.get("is_return"),
                        "return_against": invoice.get("return_against"),
                        "total_excl_tax": invoice.get("total_excl_tax"),
                        "total_tax": invoice.get("total_tax"),
                        "total_incl_tax": invoice.get("total_incl_tax"),
                        "custom_currency": invoice.get("currency"),
                        "assets_id": invoice.get("AssetsID"),
                        "financial_site_code": invoice.get("financial_site_code"),
                        "ptdrive_invoice_number": invoice.get("ptDrive Invnr"),
                        "creation": now()
                    })
                    for item in invoice.get("Item_List", []):
                        item_name = item.get("item_name", "")
                        if len(item_name) > 140:
                            item_name = item_name[:140]
                        doc.append("items", {
                                "doctype": "Imported Purchase Invoice Item",
                                "item_name": item_name,
                                "item_qty": item.get("item_qty"),
                                "item_tax": item.get("item_tax"),
                                "item_price": item.get("item_price"),
                                "stock_qty": item.get("stock_qty"),
                                "rate": item.get("rate"),
                                "amount": item.get("amount"),
                                # "income_account": item_income_account if isSiteCode else '',
                                # "expense_account": item_expense_account if isSiteCode  else '',
                        })
                    for tax in invoice.get("taxes", []):
                        account_head =tax.get("account_head")
                        if not frappe.db.exists("Account", {"name": account_head, "company": company_doc_PGT.company_name if isSiteCode else company_doc.company_name}):  ### Site_code logic for PGT company.
                            # Use the default from import_settings if account_head is not in the COA
                            account_head = company_doc_PGT.custom_account_head if isSiteCode else company_doc.custom_account_head 
                        doc.append("taxes", {
                            "doctype" : "Imported Purchase Invoice Taxes",
                            "account_head": account_head,    ### Site_code logic for PGT company.
                            ## NO NEED BY HSB => "account_head": custom_account_head_PGT if isSiteCode  else account_head,    ### Site_code logic for PGT company.
                            "description": tax.get("description"),
                            "cost_center": tax.get("cost_center"),
                            "tax_amount": tax.get("tax_amount"),
                            "total": tax.get("total")
                        })

                    # Loop through attachments and add them to child table
                    for attachment in invoice.get("attachments", []):
                        doc.append("attachments", {
                            "doctype": "Attachments",
                            "download_link": attachment.get("download_link")
                        })

                        # Save the document to ensure it has a valid name
                        if not doc.name:
                            doc.save()
                            frappe.db.commit()
                        

                        download_link = attachment.get("download_link")
                        if not download_link:
                            continue 
                        # frappe.throw(f"Downloading:{download_link}")
                        # response = requests.get(download_link) #Haseeb's Changed On 25-06-2025
                        response = requests.get(download_link, verify=False) #Haseeb's Changed On 25-06-2025
                        # frappe.throw("line 142")
                            
                        if response.status_code == 200:
                            pdf_content = response.content
                            filename = f"{invoice.get('invoice_number', 'attachment')}.pdf"

                                # Create a BytesIO object for the content
                            pdf_file = BytesIO(pdf_content)
                            _file = frappe.get_doc(
                                    {
                                        "doctype": "File",
                                        "file_name": filename,
                                        "is_private": 0,  # Set to 1 if the file should be private
                                        "content": pdf_file.getvalue(),
                                        "attached_to_doctype": "Imported Purchase Invoice",
                                        "attached_to_name": doc.name,  # Now doc.name will be valid
                            # Field in Purchase Invoice where it should be attached
                                    }
                                )
                            _file.save()
                            frappe.db.commit() 
                        
                            

                    # Save the document after adding items, taxes, and attachments
                    # doc.insert()
                    # doc.save()
                    imported_count += 1
                # Commit the transaction to the database
                frappe.db.commit()
                frappe.msgprint(f"{imported_count} Imported Purchase Invoices created successfully!")
            else:
                frappe.throw("Error in fetching data from API: " + data.get('meta', {}).get('message'))
        else:
            frappe.throw("API call failed with status code: " + str(response.status_code))

@frappe.whitelist()
def copy_bulk_imported_invoices_to_purchase(company_abbr):
    #"""Copy all non-copied Imported Purchase Invoices to Purchase Invoices or Credit Notes."""
    time_limit = datetime.now() - timedelta(days=15)    
    old_invoices = frappe.get_all(
                'Imported Purchase Invoice', 
                filters={'creation': ('<', time_limit.strftime('%Y-%m-%d %H:%M:%S'))}, 
                pluck='name'
            )
    if old_invoices:
                for invoice_name in old_invoices:
                    frappe.delete_doc('Imported Purchase Invoice', invoice_name, force=1, ignore_permissions=True)
    imported_invoices = frappe.get_all(
        "Imported Purchase Invoice",
        filters={"custom_is_copy": 0},
        pluck="name"
    )

    if not imported_invoices:
        frappe.msgprint("No new invoices to copy.")
        return
    company_name = frappe.db.get_value("Company", {"abbr": company_abbr}, "name")
    if not company_name:
        frappe.throw(f"Company with abbreviation {company_abbr} not found.")
    
    ##company_doc = frappe.get_doc('Company', company_name)  #Haseeb's Changed On 21-12-2024
    copied_count = 0  # Counter for successfully copied invoices
    skipped_count = 0  # Counter for skipped invoices

    for invoice_name in imported_invoices:
        try:
            # Fetch the imported invoice
            imported_invoice = frappe.get_doc("Imported Purchase Invoice", invoice_name)
            duplicate_invoice = frappe.db.exists(
                "Purchase Invoice",
                # {"custom_invoice_no": imported_invoice.invoice_no} #Haseeb's Changed On 21-12-2024
                {"bill_no": imported_invoice.invoice_no,
                "supplier_number": imported_invoice.supplier_code
                } #Haseeb's Changed On 21-12-2024
            )

            # duplicate_invoice = frappe.db.exists(
            #     "Purchase Invoice",
            #     # {"custom_invoice_no": imported_invoice.invoice_no} #Haseeb's Changed On 21-12-2024
            #     {"bill_no": imported_invoice.invoice_no} #Haseeb's Changed On 21-12-2024
            # ) and frappe.db.exists(
            #     "Purchase Invoice",
            #     {"supplier_number": imported_invoice.supplier_code}
            # )
            
            if duplicate_invoice:
                skipped_count += 1
                continue

            company_doc = frappe.get_doc('Company', imported_invoice.custom_company)                
            # Prepare values
            supplier_name = get_or_create_supplier(imported_invoice.supplier_name_en)

            posting_date = datetime.strptime(imported_invoice.invoice_date, '%d-%m-%Y').strftime('%Y-%m-%d')
            due_date = datetime.strptime(imported_invoice.invoice_due, '%d-%m-%Y').strftime('%Y-%m-%d')

            dateToday = date.today()
            if datetime.strptime(due_date, '%Y-%m-%d').date() < dateToday:
                due_date = datetime.today().date() + timedelta(days=1)
                due_date = due_date.strftime('%Y-%m-%d')

            if due_date < posting_date:
                # Adjust due_date to be at least one day after posting_date
                due_date = posting_date + timedelta(days=1)


            # Calculate totals with type conversion to float
            total_amount = sum(float(item.amount or 0) for item in imported_invoice.items)
            total_taxes = sum(float(tax.tax_amount or 0) for tax in imported_invoice.taxes)

            # Determine the document type and remarks
            if total_amount < 0 or total_taxes < 0:
                doc_type = "Purchase Invoice"  # Treated as Credit Note
                is_return = 1
                remarks = f"Credit Note from {imported_invoice.name}"
            else:
                doc_type = "Purchase Invoice"
                is_return = 0
                remarks = f"Imported from {imported_invoice.name}"

            # Create the Purchase Invoice or Credit Note
            purchase_invoice = frappe.get_doc({
                "doctype": doc_type,
                "supplier": supplier_name,
                "posting_date": posting_date,
                "due_date": due_date,
                "invoice_number": imported_invoice.invoice_no,
                "total": abs(total_amount),
                "total_taxes_and_charges": abs(total_taxes),
                "currency": imported_invoice.custom_currency,
                "is_return": is_return,
                "remarks": remarks,
                "custom_invoice_no" : imported_invoice.invoice_no,
                "bill_no" : imported_invoice.invoice_no, #Haseeb's Changed On 21-12-2024
                # "bill_date" : due_date, #Haseeb's Changed On 21-12-2024
                "supplier_number" :imported_invoice.supplier_code,
                "custom_complis_ptdrive_no" : imported_invoice.ptdrive_invoice_number,
                "custom_complis_company_code": imported_invoice.financial_site_code,
                "company": company_doc.name,
            })

            # Add items to the Purchase Invoice or Credit Note
            for item in imported_invoice.items:
                item_code = ensure_item_exists(item.item_name)
                qty = float(item.item_qty or 0)

                if is_return and qty > 0:
                    raise ValueError(f"Quantity for item '{item.item_name}' must be negative for a Credit Note.")

                purchase_invoice.append("items", {
                    "item_name": item.item_name,
                    "item_code" : item_code,
                    "qty": qty,
                    "rate": abs(float(item.rate or 0)),
                    "amount": float(item.amount or 0),
                    "stock_qty": float(item.stock_qty or 0),
                    "expense_account": company_doc.custom_credit_to,
                })
            
            if imported_invoice.custom_currency in ["USD", "EUR", "AED"]:
                # Fetch exchange rate from Currency Exchange doctype
                exchange_rate = frappe.db.get_value(
                    "Currency Exchange",
                    {"from_currency": imported_invoice.custom_currency},
                    "exchange_rate"
                )
                if not exchange_rate:
                    frappe.throw(_(f"Exchange rate for {imported_invoice.custom_currency} not found in Currency Exchange doctype."))
                # Set the fetched exchange rate
                purchase_invoice.conversion_rate = float(exchange_rate)
                purchase_invoice.buying_price_list = f"Buying {imported_invoice.custom_currency}"
                purchase_invoice.price_list_currency = imported_invoice.custom_currency
                purchase_invoice.plc_conversion_rate = float(exchange_rate)    

                # Fetch  Currency credit_to account detail #Haseeb's Changed On 21-12-2024
                currency_credit_to = frappe.db.get_value(
                    "Accounts Setting",
                    {"currency": imported_invoice.custom_currency},
                    "credit_to"
                )
                if not currency_credit_to: #Haseeb's Changed On 21-12-2024
                    frappe.throw(_(f"Credit_To Account not found for the Currency {imported_invoice.custom_currency}")) #Haseeb's Changed On 21-12-2024
                # purchase_invoice.credit_to = currency_credit_to #"211112 - Suppliers  - موردون -USD - POINT" #Haseeb's Changed On 21-12-2024
                # purchase_invoice.credit_to = currency_credit_to if is_return > 0 else purchase_invoice.credit_to #Haseeb's Changed On 21-12-2024
                purchase_invoice.credit_to = currency_credit_to #Haseeb's Changed On 21-12-2024


            if is_return != 1:
                # purchase_invoice.naming_series = company_doc.custom_sales_sale_series #Haseeb's Changed On 21-12-2024
                purchase_invoice.naming_series = company_doc.custom_purchase_invoice_series #Haseeb's Changed On 21-12-2024
            else :
                # purchase_invoice.naming_series = company_doc.custom_sales_return_series  #Haseeb's Changed On 21-12-2024
                purchase_invoice.naming_series = company_doc.custom_purchase_return_series  #Haseeb's Changed On 21-12-2024

            # frappe.throw('passed5')
            # Add taxes to the Purchase Invoice or Credit Note
            for tax in imported_invoice.taxes:
                account_head = tax.account_head
                if not frappe.db.exists("Account", {"name": account_head, "company": company_doc.company_name}):
                # Use the default from import_settings if account_head is not in the COA
                    account_head = company_doc.custom_account_head 
                if frappe.db.exists("Cost Center", {"name": tax.cost_center, "company": company_doc.company_name}):
                    cost_center = tax.cost_center
                else:
                    cost_center = company_doc.custom_purchase_cost_center
                purchase_invoice.append("taxes", {
                    "account_head": account_head,
                    "rate" : 15,
                    "description": tax.description,
                    "cost_center": cost_center,
                    "tax_amount": float(tax.tax_amount or 0),
                })

            # Insert the Purchase Invoice or Credit Note
            purchase_invoice.insert()
            frappe.db.commit()

            # Mark the Imported Purchase Invoice as copied
            imported_invoice.custom_is_copy = 1
            for attachment in imported_invoice.attachments:
                download_link = attachment.get("download_link")    
                if download_link:
                    # response = requests.get(download_link) #Haseeb's Changed On 25-06-2025
                    response = requests.get(download_link,verify=False)  #Haseeb's Changed On 27-06-2025
                    if response.status_code == 200:
                        pdf_content = response.content
                        filename = f"{imported_invoice.invoice_no or 'attachment'}.pdf"
                        pdf_file = BytesIO(pdf_content)
                        _file = frappe.get_doc({
                            "doctype": "File",
                            "file_name": filename,
                            "is_private": 0,
                            "content": pdf_file.getvalue(),
                            "attached_to_doctype": "Purchase Invoice",
                            "attached_to_name": purchase_invoice.name,})
                        _file.save(ignore_permissions=True)
                        frappe.db.commit()
                        purchase_invoice.reload()
                    imported_invoice.save()
                    frappe.db.commit()

            copied_count += 1  # Increment the copied count

        except Exception as e:
            frappe.log_error(message=str(e), title=f"Failed to copy {invoice_name}")
            skipped_count += 1  # Increment skipped count on failure

    # Display the results
    frappe.msgprint(f"Successfully copied {copied_count} invoices.")

@frappe.whitelist()
def copy_single_imported_invoice_to_purchase(invoice_name,force_duplicate=False):

    # """Copy a single Imported Purchase Invoice to an actual Purchase Invoice or Credit Note."""
    imported_invoice = frappe.get_doc("Imported Purchase Invoice", invoice_name)
    # frappe.throw(f"Invoice Name: {invoice_name}")
    if imported_invoice.custom_is_copy:
        frappe.msgprint(f"The invoice {invoice_name} has already been copied.")
        return False
    duplicate_invoice = frappe.db.exists(
        "Purchase Invoice",
        # {"custom_invoice_no": imported_invoice.invoice_no} #Haseeb's Changed On 21-12-2024
        {"bill_no": imported_invoice.invoice_no,
         "supplier_number": imported_invoice.supplier_code
        } #Haseeb's Changed On 21-12-2024
    # ) and frappe.db.exists(
    #     "Purchase Invoice",
    #     {"supplier_number": imported_invoice.supplier_code}
    )

    if duplicate_invoice and not force_duplicate:
        return {
            "duplicate": True,
            "message": f"Invoice {imported_invoice.invoice_no} already exists as {duplicate_invoice}. Do you want to copy it again?"}
    # Fetch the company document for the default company
    company_doc = frappe.get_doc('Company', imported_invoice.custom_company)
   

    supplier_name = get_or_create_supplier(imported_invoice.supplier_name_en)

    posting_date = datetime.strptime(imported_invoice.invoice_date, '%d-%m-%Y').strftime('%Y-%m-%d')
    due_date = datetime.strptime(imported_invoice.invoice_due, '%d-%m-%Y').strftime('%Y-%m-%d')
    
    dateToday = date.today()
    if datetime.strptime(due_date, '%Y-%m-%d').date() < dateToday:
        due_date = datetime.today().date() + timedelta(days=1)
        due_date = due_date.strftime('%Y-%m-%d')

    # Ensure due_date is not before posting_date
    if due_date < posting_date:
    # Adjust due_date to be at least one day after posting_date
        due_date = posting_date + timedelta(days=1)

    # Calculate total amount and total taxes with type conversion to float
    total_amount = sum(float(item.amount or 0) for item in imported_invoice.items)
    total_taxes = sum(float(tax.tax_amount or 0) for tax in imported_invoice.taxes)

    # Determine the document type: Purchase Invoice or Credit Note
    if total_amount < 0 or total_taxes < 0:
        doc_type = "Purchase Invoice"  # This will be stored as a Credit Note
        is_return = 1  # Mark it as a Credit Note
        remarks = f"Credit Note from {imported_invoice.name}"
    else:
        doc_type = "Purchase Invoice"
        is_return = 0
        remarks = f"Imported from {imported_invoice.name}"

    # Create a new Purchase Invoice or Credit Note
    purchase_invoice = frappe.get_doc({
        "doctype": doc_type,
        "supplier": supplier_name,
        "posting_date": posting_date,
        "due_date": due_date,
        "invoice_number": imported_invoice.invoice_no,
        "total": abs(total_amount),  # Store absolute values
        "total_taxes_and_charges": abs(total_taxes),  # Store absolute values
        "currency": imported_invoice.custom_currency,
        "is_return": is_return,  # Mark as return for Credit Note
        "remarks": remarks,
        "custom_invoice_no" : imported_invoice.invoice_no,
        "bill_no" : imported_invoice.invoice_no, #Haseeb's Changed On 21-12-2024
        "supplier_number" : imported_invoice.supplier_code, 
        "custom_complis_ptdrive_no" : imported_invoice.ptdrive_invoice_number,
        "custom_complis_company_code": imported_invoice.financial_site_code,
        "company": company_doc.name,
        
    })

    if imported_invoice.custom_currency in ["USD", "EUR", "AED"]:
        # Fetch exchange rate from Currency Exchange doctype
        exchange_rate = frappe.db.get_value(
            "Currency Exchange",
            {"from_currency": imported_invoice.custom_currency},
            "exchange_rate"
        )
        if not exchange_rate:
            frappe.throw(_(f"Exchange rate for {imported_invoice.custom_currency} not found in Currency Exchange doctype."))
        # Set the fetched exchange rate
        purchase_invoice.conversion_rate = float(exchange_rate)
        purchase_invoice.buying_price_list = f"Buying {imported_invoice.custom_currency}"
        purchase_invoice.price_list_currency = imported_invoice.custom_currency
        purchase_invoice.plc_conversion_rate = float(exchange_rate)

        # Fetch  Currency credit_to account detail #Haseeb's Changed On 21-12-2024
        currency_credit_to = frappe.db.get_value(
            "Accounts Setting",
            {"currency": imported_invoice.custom_currency},
            "credit_to"
        )
        if not currency_credit_to: #Haseeb's Changed On 21-12-2024
            frappe.throw(_(f"Credit_To Account not found for the Currency {imported_invoice.custom_currency}")) #Haseeb's Changed On 21-12-2024
        # purchase_invoice.credit_to = currency_credit_to #"211112 - Suppliers  - موردون -USD - POINT" #Haseeb's Changed On 21-12-2024
        # purchase_invoice.credit_to = currency_credit_to if is_return > 0 else purchase_invoice.credit_to #Haseeb's Changed On 21-12-2024
        purchase_invoice.credit_to = currency_credit_to #Haseeb's Changed On 21-12-2024

    if is_return != 1:
        # purchase_invoice.naming_series = company_doc.custom_sales_invoice_series #Haseeb's Changed On 21-12-2024
        purchase_invoice.naming_series = company_doc.custom_purchase_invoice_series #Haseeb's Changed On 21-12-2024
    else :  
        # purchase_invoice.naming_series = company_doc.custom_sales_return_series #Haseeb's Changed On 21-12-2024
        purchase_invoice.naming_series = company_doc.custom_purchase_return_series #Haseeb's Changed On 21-12-2024

    # Add items to the Purchase Invoice or Credit Note
    for item in imported_invoice.items:
        # Ensure quantity is correctly converted to float
        item_code = ensure_item_exists(item.item_name)
        try:
            qty = float(item.item_qty or 0)
        except ValueError:
            frappe.throw(f"Invalid quantity '{item.item_qty}' for item '{item.item_name}'.")

        # If it's a Credit Note, quantity should be negative
        if is_return and qty > 0:
            frappe.throw(f"Quantity for item '{item.item_name}' must be negative for a Credit Note.")

        purchase_invoice.append("items", {
            "item_name": item.item_name,
            "item_code" : item_code,
            "qty":qty,  # Use absolute quantity for consistency
            "rate": float(item.rate or 0),
            "amount": float(item.amount or 0),  # Use absolute amount
            "stock_qty": float(item.stock_qty or 0),  # Use absolute stock quantity
            "expense_account": company_doc.custom_credit_to,
        })





    # Add taxes to the Purchase Invoice or Credit Note
    for tax in imported_invoice.taxes:
        account_head = tax.account_head
        if not frappe.db.exists("Account", {"name": account_head, "company": company_doc.company_name}):
            account_head = company_doc.custom_account_head 
        if frappe.db.exists("Cost Center", {"name": tax.cost_center, "company": company_doc.company_name}):
            cost_center = tax.cost_center
        else:
            cost_center = company_doc.custom_purchase_cost_center     




        purchase_invoice.append("taxes", {
            "account_head": account_head,
            "rate" : 15,
            "description": tax.description,
            "cost_center": cost_center,
            "tax_amount": float(tax.tax_amount or 0),  # Use absolute tax amount
        })
    # Insert the new Purchase Invoice or Credit Note

    # frappe.throw(imported_invoice.custom_currency)
    # frappe.msgprint(f"purchase_invoice company: {purchase_invoice.company}")
    # return 

    purchase_invoice.insert()
    frappe.db.commit()

    # Mark the Imported Purchase Invoice as copied
    imported_invoice.custom_is_copy = 1
    imported_invoice.save()
    for attachment in imported_invoice.attachments:
        download_link = attachment.get("download_link")    
        if download_link:
            # response = requests.get(download_link) #Haseeb's Changed On 25-06-2025
            response = requests.get(download_link, verify=False) #Haseeb's Changed On 25-06-2025
            if response.status_code == 200:
                pdf_content = response.content
                filename = f"{imported_invoice.invoice_no or 'attachment'}.pdf"
                pdf_file = BytesIO(pdf_content)
                _file = frappe.get_doc({
                    "doctype": "File",
                    "file_name": filename,
                    "is_private": 0,
                    "content": pdf_file.getvalue(),
                    "attached_to_doctype": "Purchase Invoice",
                    "attached_to_name": purchase_invoice.name,})
                _file.save(ignore_permissions=True)
                frappe.db.commit()
                purchase_invoice.reload()
    frappe.db.commit()

    frappe.msgprint(f"Successfully copied to {doc_type}: {purchase_invoice.name}")
    return True

def get_or_create_supplier(supplier_name_en):
    """Ensure the supplier exists or use the existing one."""
    supplier = frappe.db.get_value("Supplier", {"supplier_name": supplier_name_en}, "name")

    if supplier:
        return supplier

    supplier_doc = frappe.get_doc({
        "doctype": "Supplier",
        "supplier_name": supplier_name_en
    })
    supplier_doc.insert()
    frappe.msgprint(f"Created new supplier: {supplier_name_en}")
    return supplier_doc.name
    
def ensure_item_exists(item_name):
    """Ensure the item exists in the Item doctype; if not, create it."""
    existing_item = frappe.db.get_value("Item", {"item_name": item_name, "is_stock_item": 0}, "item_code")
    if existing_item:
        return existing_item
    # if not frappe.db.exists("Item", {"item_name": item_name}):
    else:
        new_item = frappe.get_doc({
            "doctype": "Item",
            "item_name": item_name,
            "item_group": "Services",  # Default item group
            "is_stock_item": 0,  # Not a stock item
        })
        new_item.insert()
        frappe.db.commit()
    return new_item.item_code

##############################################################
###-START=> TO SCHEDULE THE SYNC PURCHASE JOB WRITTEN BY HASEEB
##############################################################
from alw.alw.helpers import get_current_date_time
def schedule_purchase_import():
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
            company_doc.custom_sync_start =  get_current_date_time(5, "00:00:01")
            company_doc.custom_sync_end = get_current_date_time(0, "23:59:59")
            company_doc.save()  ##Save the changes
            frappe.db.commit()  ##Commit the transaction

            fetch_and_store_imported_purchase_invoices(company_abbr) ##Fetching Invoices
            copy_bulk_imported_invoices_to_purchase(company_abbr) ##POSTING IMPORTED INVOICE INTO INVOICE DOCTYPE

            return got_company_name
    except Exception as e:
        frappe.throw(str(e) + " COMPANY: " + company_abbr)
##############################################################
###-END=> TO SCHEDULE THE SYNC PURCHASE JOB WRITTEN BY HASEEB
##############################################################



##############################################################
###-START=> API FOR PURCHASE INVOICES WRITTEN BY HASEEB
    # API Calls:  
        # bench execute alw.alw.purchase.piapi --kwargs '{"date_from":"2025-01-01","date_to":"2025-01-20"}'
        # curl -X POST   https://erp.tzamun.sa/api/method/alw.alw.purchase.piapi   -H "Content-Type: application/json"   -d '{"date_from":"2025-01-01", "date_to":"2025-01-20"}'
        # curl -X POST   https://erp.tzamun.sa/api/method/alw.alw.purchase.piapi   -H "Content-Type: application/json"   -H "Authorization: token <api-key>:<api-secret>"   -d '{"date_from":"2025-01-01", "date_to":"2025-01-20"}'
    # Returns a list of Purchase Invoices between DateFrom and DateTo.
    # :param date_from: Start date (YYYY-MM-DD)
    # :param date_to: End date (YYYY-MM-DD)
    # :return: List of Purchase Invoices
##############################################################
import frappe
from frappe.utils import getdate


@frappe.whitelist(allow_guest=True)
def piapi(key,date_from,date_to):

    company_abbr="POINT"
    company_name = frappe.db.get_value("Company", {"abbr": company_abbr}, "name")
    date_from = getdate(date_from)
    date_to = getdate(date_to)
    # date_from = getdate('2025-01-01')
    # date_to = getdate('2025-01-31')
    base_url = frappe.utils.get_url()
    try:
        api = frappe.get_attr("alw.alw.apikey.validate_key_piapi")
        response = api(key)
        if response.get("valid") == "0":
            return {"status": "error", "message": "Invalid API key validation"}
        else:
            invoices = frappe.get_all(
                "Purchase Invoice",
                filters={
                    "posting_date": ["between", [date_from, date_to]],
                    #"status": ["in", ["Paid", "Submitted","Overdue"]],
                    "company": company_name  # Fetch only selected company
                },
                fields=["company", "name", "status","supplier", "supplier_number","supplier_name","posting_date", "custom_complis_ptdrive_no","custom_complis_company_code","bill_no","total","taxes_and_charges_added","grand_total","currency","is_return"]
            )
            if not invoices: ## RECORD NOT FOUND
                return {"code":"210","status": "Success", "message": "Record Not Found"}
            else: ## RECORD FOUND
                # Iterate through the invoices and set null values to empty string
                for invoice in invoices:
                    # Set default empty strings if the fields are None
                    if invoice.get('custom_complis_ptdrive_no') is None:
                        invoice['custom_complis_ptdrive_no'] = ''
                    if invoice.get('custom_complis_company_code') is None:
                        invoice['custom_complis_company_code'] = ''

                    # Fetch all attachments for the current invoice
                    base_url = frappe.utils.get_url()
                    attachments = frappe.get_all(
                        "File",
                        filters={
                            "attached_to_doctype": "Purchase Invoice",
                            "attached_to_name": invoice["name"]
                        },
                        fields=["name","file_name", "file_url","is_private"]
                    )
                
                #    # Ensure the file_url is absolute
                #     for attachment in attachments:
                #         file_url = attachment['file_url']  # Make sure to start with the current file_url

                #         # Update the File doctype if the file is private
                #         if attachment.get("is_private", 0) == 1:
                #             file_doc = frappe.get_doc("File", attachment["name"])
                #             file_doc.is_private = 0  # Set to public
                #             file_doc.save(ignore_permissions=True)
                #             frappe.db.commit()
                #             file_url = attachment['file_url'].replace("/private/files/", "/files/")  # Update the path to public folder

                #         # Ensure the file_url is absolute
                #         if not file_url.startswith(("http://", "https://")):
                #             attachment["file_url"] = f"{base_url}{file_url}"
                #         else:
                #             # If it's already an absolute URL, just update the attachment file_url
                #             attachment["file_url"] = file_url

                #     # Add the attachments to the invoice dictionary
                #     invoice["attachments"] = attachments

                return {"code":"200","status": "success", "data": invoices}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "piapi")
        return {"code":"400","status": "error", "message": str(e)}
##############################################################
###-END=> API FOR PURCHASE INVOICES WRITTEN BY HASEEB
##############################################################

