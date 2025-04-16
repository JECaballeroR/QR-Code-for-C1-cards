import streamlit as st
from PIL import Image, ImageDraw
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from io import BytesIO

# App title
st.title("QR Code Generator with Logo and Rounded Eyes")
st.markdown("Enter a full URL (e.g., a `.vcf` file), and generate a custom QR code with a logo.")

# Input
url = st.text_input("URL to link to", value="https://www.correlation-one.com/hubfs/EstebanCaballero.vcf")
generate = st.button("Generate QR Code")

if generate and url:
    name = "GeneratedQR"
    logo_path = "C1 Short Logo Dark@2x.png"

    # Create the QR Code object
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Generate QR image with rounded modules
    qr_img_rgb = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color="#000000",
        back_color="white"
    ).convert("RGB")

    # Draw custom rounded eyes
    draw = ImageDraw.Draw(qr_img_rgb)
    module_px = qr.box_size
    eye_size_modules = 7
    eye_px = eye_size_modules * module_px
    dot_size = 3 * module_px
    dot_radius = dot_size // 2

    eye_positions = [
        (qr.border * module_px, qr.border * module_px),  # Top-left
        (qr_img_rgb.size[0] - qr.border * module_px - eye_px, qr.border * module_px),  # Top-right
        (qr.border * module_px, qr_img_rgb.size[1] - qr.border * module_px - eye_px),  # Bottom-left
    ]

    for x, y in eye_positions:
        draw.rectangle([x, y, x + eye_px, y + eye_px], fill="white")
        draw.rounded_rectangle([x, y, x + eye_px, y + eye_px], radius=25, fill="#000000")
        inner_padding = module_px
        draw.rounded_rectangle(
            [x + inner_padding, y + inner_padding, x + eye_px - inner_padding, y + eye_px - inner_padding],
            radius=20,
            fill="white"
        )
        dot_center_x = x + eye_px // 2
        dot_center_y = y + eye_px // 2
        draw.ellipse(
            [
                (dot_center_x - dot_radius, dot_center_y - dot_radius),
                (dot_center_x + dot_radius, dot_center_y + dot_radius)
            ],
            fill="#000000"
        )

    # Center and paste the logo
    logo = Image.open(logo_path)
    qr_width = qr_img_rgb.size[0]
    aspect_ratio = logo.width / logo.height
    target_height = int(qr_width * 0.15)
    target_width = int(target_height * aspect_ratio)
    logo = logo.resize((target_width, target_height), Image.LANCZOS)

    padding = 10
    logo_bg = Image.new("RGB", (target_width + 2 * padding, target_height + 2 * padding), "white")
    logo_bg.paste(logo, (padding, padding), mask=logo if logo.mode == 'RGBA' else None)

    pos = ((qr_width - logo_bg.width) // 2, (qr_width - logo_bg.height) // 2)
    qr_img_rgb.paste(logo_bg, pos)

    # Display QR code image
    st.image(qr_img_rgb, caption="Generated QR Code", use_container_width=False)

    # Prepare image for download
    buf = BytesIO()
    qr_img_rgb.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="📥 Download QR as PNG",
        data=byte_im,
        file_name=f"{name}.png",
        mime="image/png"
    )
