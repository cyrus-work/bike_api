import qrcode

# Dynamic Link
dynamic_link = "https://play.google.com/store/apps/details?id=io.cyruslab.bike"

# QR 코드 생성
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(dynamic_link)
qr.make(fit=True)

# QR 코드 이미지 생성
img = qr.make_image(fill='black', back_color='white')
img.save("app_install_bluetooth_connect.png")
img.show()
