# convert.py
import io
import base64
from flask import Blueprint, request, jsonify, current_app, send_file
from PIL import Image

convert_bp = Blueprint("convert_bp", __name__)

# Pillow-supported formats
SUPPORTED_FORMATS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "webp": "WEBP",
    "bmp": "BMP",
    "tiff": "TIFF",
    # "heic": "HEIC"  # needs pillow-heif or pyheif
}

@convert_bp.route("/convert", methods=["POST"])
def convert_images():
    """
    Endpoint to convert multiple images to a specified format.

    Expects:
      - form-data with key "images" (multiple accepted)
      - form-data with key "target_format" (e.g. 'png', 'jpg', 'gif')

    Returns:
      JSON:
      {
        "images": [
          { "filename": "...", "converted_b64": "..." },
          ...
        ]
      }
      Each item includes the base64-encoded image data in the new format.

    If more than 5 images are provided, returns an error.
    """
    current_app.logger.info("Convert endpoint hit (multi-file)")

    try:
        # Grab target format
        target_format = request.form.get("target_format", "png").lower()
        if target_format not in SUPPORTED_FORMATS:
            current_app.logger.error(f"Unsupported format requested: {target_format}")
            return jsonify({"error": f"Unsupported format: {target_format}"}), 400

        pillow_format = SUPPORTED_FORMATS[target_format]
        current_app.logger.info(f"Converting to Pillow format: {pillow_format}")

        # Grab up to 5 images
        files = request.files.getlist("images")
        if not files:
            current_app.logger.warning("No images provided for convert.")
            return jsonify({"error": "No images provided"}), 400

        if len(files) > 5:
            current_app.logger.warning(f"Received {len(files)} images, exceeding the limit of 5.")
            return jsonify({"error": "Max 5 images allowed"}), 400

        converted_results = []
        for file in files:
            filename = file.filename or "image"
            current_app.logger.info(f"Converting file: {filename}")

            image = Image.open(file.stream)

            # Convert to RGB if needed for certain formats (like JPEG)
            # If user wants PNG/GIF, we might keep RGBA. 
            # But to keep consistent, let's do a simple approach:
            # If user requested JPEG, we must ensure "RGB".
            if pillow_format == "JPEG" and image.mode not in ["RGB", "L", "1"]:
                current_app.logger.info(f"Converting from {image.mode} to RGB for {filename}")
                image = image.convert("RGB")

            # Save to in-memory buffer
            output = io.BytesIO()
            image.save(output, format=pillow_format)
            output.seek(0)

            b64_data = base64.b64encode(output.read()).decode("utf-8")
            converted_results.append({
                "filename": filename,
                "converted_b64": b64_data
            })

        current_app.logger.info(f"Successfully converted {len(converted_results)} images.")
        return jsonify({"images": converted_results})

    except Exception as e:
        current_app.logger.error(f"Error in /convert: {e}")
        return jsonify({"error": f"Convert error: {str(e)}"}), 500