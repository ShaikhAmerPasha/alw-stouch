import io
from base64 import b64encode
from pyqrcode import create as qr_create
import frappe
from datetime import datetime

def encode_tlv(tag: int, value: str) -> str:
    value_bytes = value.encode("utf-8")
    return bytes([tag]).hex() + bytes([len(value_bytes)]).hex() + value_bytes.hex()

@frappe.whitelist(allow_guest=True)
def generate_zatca_qr_code_api(company, tax_number, date, total, tax_amount):
    try:
        # Validate inputs (optional)
        if not (company and tax_number and date and total and tax_amount):
            frappe.local.response['http_status_code'] = 400
            frappe.local.response['message'] = "Missing required parameters."
            return

        tlv_array = []
        tlv_array.append(encode_tlv(1, company))
        tlv_array.append(encode_tlv(2, tax_number))
        tlv_array.append(encode_tlv(3, date))
        tlv_array.append(encode_tlv(4, str(total)))
        tlv_array.append(encode_tlv(5, str(tax_amount)))

        tlv_hex = "".join(tlv_array)
        tlv_base64 = b64encode(bytes.fromhex(tlv_hex)).decode()

        # Generate QR code
        qr_image = io.BytesIO()
        url = qr_create(tlv_base64, error="L")
        url.png(qr_image, scale=4, quiet_zone=1)
        qr_image.seek(0)

        filename = f"zatca_qr_{tax_number}_{date}_{datetime.now().strftime('%H%M%S')}.png"
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = qr_image.getvalue()
        frappe.local.response.type = "download"
        frappe.local.response.mimetype = "image/png"
        return

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "ZATCA QR Code API Error")
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['message'] = str(e)
        return
