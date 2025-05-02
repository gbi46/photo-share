from io import BytesIO

import base64
import qrcode

class QrCodeService:
    @staticmethod
    def generate_qr_code(url: str) -> str:
        img = qrcode.make(url)
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        qr_code_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        qr_code = f"data:image/png;base64,{qr_code_base64}"
        
        return {"qr_code": qr_code, "qr_code_url": url}