
import frappe
from frappe import _
from frappe.utils.response import Response
from frappe.utils import formatdate, flt
import json
from datetime import datetime, date, timedelta


# @frappe.whitelist(allow_guest=True)
# def get_sales_invoice_details(sales_invoice_name):
#     try:
#         # Fetch the sales invoice document
#         sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)

#         # Serialize the sales invoice data into a dictionary
#         sales_invoice_data = convert_to_serializable(sales_invoice.as_dict())

#         # Return the data as a JSON response
#         return Response(
#             json.dumps({"data": sales_invoice_data}),
#             status=200,
#             mimetype='application/json'
#         )
#     except frappe.DoesNotExistError:
#         return Response(
#             json.dumps({"error": _("Sales Invoice not found.")}),
#             status=404,
#             mimetype='application/json'
#         )
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Error in get_sales_invoice_details")
#         return Response(
#             json.dumps({"error": str(e)}),
#             status=500,
#             mimetype='application/json'
#         )

def convert_to_serializable(data):
    """Recursively converts datetime, date, and timedelta objects to strings."""
    if isinstance(data, dict):
        return {key: convert_to_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]
    elif isinstance(data, (datetime, date)):
        return data.strftime('%Y-%m-%d')  # Convert to string
    elif isinstance(data, timedelta):
        # Convert timedelta to string representation in hours, minutes, and seconds
        return str(data)
    else:
        return data
@frappe.whitelist(allow_guest=True)
def get_sales_invoices_by_date_range(start_date, end_date):
    try:
        # Fetch Sales Invoices filtered by a range of posting dates
        sales_invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "posting_date": ["between", [start_date, end_date]]
            },
            fields=["*"]
        )

        # Serialize each sales invoice document into a dictionary
        sales_invoices_data = [
            convert_to_serializable(frappe.get_doc("Sales Invoice", inv.name).as_dict()) for inv in sales_invoices
        ]

        # Return the data as a JSON response
        return Response(
            json.dumps({"data": sales_invoices_data}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_sales_invoices_by_date_range")
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )



@frappe.whitelist(allow_guest=True)
def get_purchase_invoices_by_date_range(start_date, end_date):
    try:
        # Fetch Purchase Invoices filtered by a range of posting dates
        purchase_invoices = frappe.get_all(
            "Purchase Invoice",
            filters={
                "posting_date": ["between", [start_date, end_date]]
            },
            fields=["*"]
        )

        # Serialize each purchase invoice document into a dictionary
        purchase_invoices_data = [
            convert_to_serializable(frappe.get_doc("Purchase Invoice", inv.name).as_dict()) for inv in purchase_invoices
        ]

        # Return the data as a JSON response
        return Response(
            json.dumps({"data": purchase_invoices_data}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_purchase_invoices_by_date_range")
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )
