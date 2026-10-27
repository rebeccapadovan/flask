import os
import uuid

from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename
from flask import current_app

MAX_IMAGE_BYTES = 5 * 1024 * 1024

ALLOWED_FORMATS = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}


def save_image(file):
    if not file or not file.filename:
        return None

    safe_name = secure_filename(file.filename)
    extension = os.path.splitext(safe_name)[1].lower()

    if not safe_name or extension not in ALLOWED_FORMATS:
        raise ValueError(
            "Envie uma imagem JPG, JPEG, PNG ou WEBP."
        )

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)

    if size > MAX_IMAGE_BYTES:
        raise ValueError("A imagem deve ter no máximo 5 MB.")

    try:
        image = Image.open(file.stream)

        if image.format != ALLOWED_FORMATS[extension]:
            raise ValueError(
                "A extensão do arquivo não corresponde à imagem."
            )

        image.verify()
        file.stream.seek(0)

    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ValueError("O arquivo enviado não é uma imagem válida.")

    filename = f"{uuid.uuid4().hex}{extension}"
    upload_folder = os.path.join(
        current_app.root_path, "static", "uploads"
    )
    os.makedirs(upload_folder, exist_ok=True)

    file.save(os.path.join(upload_folder, filename))

    return filename
