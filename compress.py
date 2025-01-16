# compress.py
import io
import base64
from flask import Blueprint, request, jsonify, current_app
from PIL import Image

compress_bp = Blueprint("compress_bp", __name__)

@compress_bp.route("/compress", methods=["POST"])
def compress_images():
    """
    Endpoint to compress one or more images at once.

    Expects:
      - form-data with key "images" for the files (multiple accepted)
      - form-data with key "compression_level" (integer 1..10)

    Returns:
      JSON with structure:
      {
        "images": [
          { "filename": "...", "compressed_b64": "..." },
          ...
        ]
      }
      Each item includes the base64-encoded compressed JPEG.

    If more than 5 images are provided, returns an error.
    """
    current_app.logger.info("Compress endpoint hit (multi-file)")

    try:
        # 1) Grab the compression level
        compression_str = request.form.get("compression_level", "5")
        compression_level = int(compression_str)
        quality = min(max(compression_level * 10, 1), 100)
        current_app.logger.info(f"Compression level {compression_level}, JPEG quality = {quality}")

        # 2) Grab the list of files under 'images' (multiple files)
        files = request.files.getlist("images")
        if not files or len(files) == 0:
            current_app.logger.warning("No image files provided in the request")
            return jsonify({"error": "No image files provided"}), 400

        if len(files) > 5:
            current_app.logger.warning(f"Received {len(files)} images, exceeding the limit of 5.")
            return jsonify({"error": "Max 5 images allowed"}), 400

        compressed_results = []

        for file in files:
            filename = file.filename or "image.jpg"
            current_app.logger.info(f"Compressing file: {filename}")

            # 3) Load image
            image = Image.open(file.stream)

            # Convert to RGB if needed (e.g. P, RGBA, CMYK modes)
            if image.mode not in ["RGB", "L", "1"]:
                current_app.logger.info(f"Converting from {image.mode} to RGB for {filename}")
                image = image.convert("RGB")

            # 4) Compress & save to an in-memory buffer as JPEG
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=quality)
            output.seek(0)

            # 5) Convert the compressed output to base64 for JSON return
            b64_data = base64.b64encode(output.read()).decode("utf-8")

            compressed_results.append({
                "filename": filename,
                "compressed_b64": b64_data
            })

        current_app.logger.info(f"Successfully compressed {len(compressed_results)} images.")
        return jsonify({"images": compressed_results})

    except Exception as e:
        current_app.logger.error(f"Error in /compress: {e}")
        return jsonify({"error": f"Compression error: {str(e)}"}), 500