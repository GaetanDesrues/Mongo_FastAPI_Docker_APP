import qrcode
from io import BytesIO
from PIL import Image

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=1,
)

data = "This is a text"
qr.add_data(data)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
# img.save("qrcode.png")
# img.show()

byte_stream = BytesIO()
img.save(byte_stream, format="PNG")
qr_code_bytes = byte_stream.getvalue()

byte_stream = BytesIO(qr_code_bytes)
img = Image.open(byte_stream)
img.show()
# img.save("qrcode_b.png")
