import io
import base64
from flask import Blueprint, request, jsonify, current_app
from PIL import Image

favicon_bp = Blueprint("favicon_bp", __name__)

@favicon_bp.route("/favicon", methods=["POST"])
def generate_favicons():
    """
    Endpoint to create multiple favicons from multiple images.

    Expects:
      - form-data with key "images" (the files, up to 5).
      - For each image, we'll generate:
         1) 16x16 PNG
         2) 32x32 PNG
         3) ICO (32x32 inside .ico)

    Returns JSON:
      {
        "images": [
          {
            "filename": "...",
            "fav16_b64": "...",
            "fav32_b64": "...",
            "ico_b64": "..."
          },
          ...
        ]
      }
    """
    current_app.logger.info("Favicon endpoint hit (multi-file)")
    try:
        files = request.files.getlist("images")
        if not files:
            current_app.logger.warning("No images provided for favicon.")
            return jsonify({"error": "No images provided"}), 400

        if len(files) > 5:
            current_app.logger.warning(f"Received {len(files)} images, exceeding the limit of 5.")
            return jsonify({"error": "Max 5 images allowed"}), 400

        results = []
        for file in files:
            filename = file.filename or "image"
            current_app.logger.info(f"Generating favicon for file: {filename}")

            image = Image.open(file.stream).convert("RGBA")

            # Create 16x16 PNG
            fav16_img = image.resize((16, 16), Image.Resampling.LANCZOS)
            output16 = io.BytesIO()
            fav16_img.save(output16, format="PNG")
            output16.seek(0)
            fav16_b64 = base64.b64encode(output16.read()).decode("utf-8")

            # Create 32x32 PNG
            fav32_img = image.resize((32, 32), Image.Resampling.LANCZOS)
            output32 = io.BytesIO()
            fav32_img.save(output32, format="PNG")
            output32.seek(0)
            fav32_b64 = base64.b64encode(output32.read()).decode("utf-8")

            # Create .ico (32x32 inside ICO)
            ico_output = io.BytesIO()
            fav32_img.save(ico_output, format="ICO")
            ico_output.seek(0)
            ico_b64 = base64.b64encode(ico_output.read()).decode("utf-8")

            results.append({
                "filename": filename,
                "fav16_b64": fav16_b64,
                "fav32_b64": fav32_b64,
                "ico_b64": ico_b64
            })

        current_app.logger.info(f"Successfully generated favicons for {len(results)} images.")
        return jsonify({"images": results})

    except Exception as e:
        current_app.logger.error(f"Error in /favicon: {e}")
        return jsonify({"error": f"Favicon error: {str(e)}"}), 500
