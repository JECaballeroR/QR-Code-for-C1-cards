import streamlit as st
from PIL import Image, ImageDraw
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from io import BytesIO

# App title
st.title("Generador de QR con Logo y Ojos Redondeados")
st.markdown("Ingresa una URL (por ejemplo, un `.vcf`) y genera un código QR personalizado.")

# Input
url = st.text_input("URL del archivo o página", value="https://www.correlation-one.com/hubfs/EstebanCaballero.vcf")
generate = st.button("Generar QR")

if generate and url:
    name = "GeneratedQR"
    logo_path = "C1 Short Logo Dark@2x.png"

    # Crear QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img_rgb = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color="#000000",
        back_color="white"
    ).convert("RGB")

    # Dibujar ojos
    draw = ImageDraw.Draw(qr_img_rgb)
    module_px = qr.box_size
    eye_size_modules = 7
    eye_px = eye_size_modules * module_px
    dot_size = 3 * module_px
    dot_radius = dot_size // 2

    eye_positions = [
        (qr.border * module_px, qr.border * module_px),
        (qr_img_rgb.size[0] - qr.border * module_px - eye_px, qr.border * module_px),
        (qr.border * module_px, qr_img_rgb.size[1] - qr.border * module_px - eye_px),
    ]

    for x, y in eye_positions:
        draw.rectangle([x, y, x + eye_px, y + eye_px], fill="white")
        draw.rounded_rectangle([x, y, x + eye_px, y + eye_px], radius=30, fill="#000000")
        inner_padding = module_px
        draw.rounded_rectangle(
            [x + inner_padding, y + inner_padding, x + eye_px - inner_padding, y + eye_px - inner_padding],
            radius=10,
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

    # Logo centrado
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

    # Mostrar imagen en Streamlit
    st.image(qr_img_rgb, caption="QR generado", use_column_width=False)

    # Preparar descarga
    buf = BytesIO()
    qr_img_rgb.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="📥 Descargar QR como PNG",
        data=byte_im,
        file_name=f"{name}.png",
        mime="image/png"
    )
