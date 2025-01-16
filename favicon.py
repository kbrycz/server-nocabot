# favicon.py
from flask import Blueprint, request, send_file, current_app
from PIL import Image
import io

favicon_bp = Blueprint("favicon_bp", __name__)

@favicon_bp.route("/favicon", methods=["POST"])
def generate_favicon():
    """
    Endpoint to create a favicon from an image.
    
    Expects:
      - form-data with key "image" (the file)
      - optionally we could accept size param, but typically favicons are 16x16, 32x32, etc.

    Returns:
      - A .ico file or a PNG file with the correct favicon size.
    """
    current_app.logger.info("Favicon endpoint hit")
    try:
        current_app.logger.info(f"Request content type: {request.content_type}")

        image_file = request.files.get("image")
        if not image_file:
            current_app.logger.warning("No image file provided for favicon generation")
            return "No image file provided", 400

        # Load the image
        image = Image.open(image_file.stream).convert("RGBA")

        # Common favicon sizes are 16x16, 32x32, 48x48, etc.
        # We'll pick 32x32 for demonstration
        size = (32, 32)
        resized_img = image.resize(size, Image.Resampling.LANCZOS)

        # We can either return a .ico or a PNG:
        # 1) Returning an .ico:
        output = io.BytesIO()
        # We can save multiple sizes in an ICO, but let's keep it simple
        resized_img.save(output, format="ICO")
        output.seek(0)

        current_app.logger.info("Favicon generated, sending .ico")
        return send_file(
            output,
            mimetype="image/x-icon",
            as_attachment=True,
            download_name="favicon.ico"
        )

        # Or if you prefer PNG-based approach:
        # output = io.BytesIO()
        # resized_img.save(output, format="PNG")
        # output.seek(0)
        # return send_file(
        #     output,
        #     mimetype="image/png",
        #     as_attachment=True,
        #     download_name="favicon.png"
        # )
    except Exception as e:
        current_app.logger.error(f"Error in /favicon: {e}")
        return f"Favicon error: {str(e)}", 500