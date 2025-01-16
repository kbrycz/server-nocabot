from flask import Blueprint, request, send_file, current_app
from PIL import Image
import io

resize_bp = Blueprint("resize_bp", __name__)

@resize_bp.route("/resize", methods=["POST"])
def resize_image():
    """
    Endpoint to resize an image.

    Expects:
      - form-data with key "image" for the file
      - form-data with key "width" (int)
      - form-data with key "height" (int)

    Returns:
      - Resized image as an attachment (MIME type image/jpeg)
    """
    current_app.logger.info("Resize endpoint hit")
    try:
        current_app.logger.info(f"Request received with content type: {request.content_type}")

        image_file = request.files.get("image")
        if not image_file:
            current_app.logger.warning("No image file provided for resizing")
            return "No image file provided", 400

        # Convert requested width/height from strings to int
        width_str = request.form.get("width", "0")
        height_str = request.form.get("height", "0")

        width = int(width_str)
        height = int(height_str)
        current_app.logger.info(f"Requested resize to: {width} x {height}")

        # Load image with Pillow
        image = Image.open(image_file.stream)

        # Perform the actual resize
        # LANCZOS is a high-quality resampling filter
        resized_image = image.resize((width, height), resample=Image.Resampling.LANCZOS)

        # Save the resized image to an in-memory buffer
        output = io.BytesIO()
        resized_image.save(output, format="JPEG")
        output.seek(0)

        current_app.logger.info("Image successfully resized, sending response")
        return send_file(
            output,
            mimetype="image/jpeg",
            as_attachment=True,
            download_name="resized.jpg"
        )
    except Exception as e:
        current_app.logger.error(f"Error in /resize: {e}")
        return f"Resize error: {str(e)}", 500