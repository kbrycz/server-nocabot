from flask import Blueprint, request, send_file, current_app
from PIL import Image
import io

convert_bp = Blueprint("convert_bp", __name__)

# A mapping from user-facing string (e.g. 'jpg') to Pillow format name (e.g. 'JPEG')
# You can add or remove as needed. Pillow supports these formats by default, minus HEIC.
SUPPORTED_FORMATS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "webp": "WEBP",
    "bmp": "BMP",
    "tiff": "TIFF",
    # "heic": "HEIC"  # Would need pillow-heif or something similar
}

@convert_bp.route("/convert", methods=["POST"])
def convert_image():
    """
    Endpoint to convert an image to a specified format.

    Expects:
      - form-data with key "image" (the file)
      - form-data with key "target_format" (string: e.g. 'png', 'jpg', 'gif', ...)

    Returns:
      - The converted image as an attachment (mimetype depends on format)
    """
    current_app.logger.info("Convert endpoint hit")
    try:
        current_app.logger.info(f"Request received with content type: {request.content_type}")

        # Grab the uploaded file
        image_file = request.files.get("image")
        if not image_file:
            current_app.logger.warning("No image file provided in the request")
            return "No image file provided", 400

        # Grab the target format
        target_format = request.form.get("target_format", "png").lower()
        current_app.logger.info(f"Requested target format: {target_format}")

        # Check if it's supported
        if target_format not in SUPPORTED_FORMATS:
            current_app.logger.error(f"Unsupported format requested: {target_format}")
            return f"Unsupported target format: {target_format}", 400

        pillow_format = SUPPORTED_FORMATS[target_format]
        current_app.logger.info(f"Converting to Pillow format: {pillow_format}")

        # Load the image
        image = Image.open(image_file.stream)

        # Convert & save to an in-memory buffer
        output = io.BytesIO()
        image.save(output, format=pillow_format)
        output.seek(0)

        # Choose a suitable file extension
        file_extension = target_format if target_format != "jpeg" else "jpg"
        download_name = f"converted.{file_extension}"

        current_app.logger.info("Image successfully converted, sending response")
        # Return the file
        # We'll guess the mimetype from the format. Typically 'image/jpeg', 'image/png', etc.
        mimetype_map = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "GIF": "image/gif",
            "WEBP": "image/webp",
            "BMP": "image/bmp",
            "TIFF": "image/tiff",
            # "HEIC": "image/heic"   # if using pillow-heif, for example
        }
        final_mime = mimetype_map.get(pillow_format, "application/octet-stream")

        return send_file(
            output,
            mimetype=final_mime,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        current_app.logger.error(f"Error in /convert: {e}")
        return f"Convert error: {str(e)}", 500