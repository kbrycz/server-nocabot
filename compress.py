from flask import Blueprint, request, send_file, current_app
from PIL import Image
import io

compress_bp = Blueprint("compress_bp", __name__)

@compress_bp.route("/compress", methods=["POST"])
def compress_image():
    """
    Endpoint to compress an image.

    Expects:
      - form-data with key "image" for the file
      - form-data with key "compression_level" (integer 1..10)

    Returns:
      - Compressed image as an attachment (MIME type image/jpeg)
    """
    current_app.logger.info("Compress endpoint hit")
    try:
        current_app.logger.info(f"Request received with content type: {request.content_type}")

        image_file = request.files.get("image")
        if not image_file:
            current_app.logger.warning("No image file provided in the request")
            return "No image file provided", 400

        compression_str = request.form.get("compression_level", "5")
        compression_level = int(compression_str)
        current_app.logger.info(f"Compression level received: {compression_level}")

        # Load the image using Pillow
        image = Image.open(image_file.stream)

        # Convert compression_level (1..10) to JPEG quality (1..100)
        quality = min(max(compression_level * 10, 1), 100)
        current_app.logger.info(f"Calculated JPEG quality: {quality}")

        # Compress & save to an in-memory buffer
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=quality)
        output.seek(0)

        current_app.logger.info("Image successfully compressed, sending response")
        return send_file(
            output,
            mimetype="image/jpeg",
            as_attachment=True,
            download_name="compressed.jpg"
        )
    except Exception as e:
        current_app.logger.error(f"Error in /compress: {e}")
        return f"Compression error: {str(e)}", 500