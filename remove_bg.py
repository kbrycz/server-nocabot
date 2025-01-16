# # remove_bg.py
# # pip install rembg
# from flask import Blueprint, request, send_file, current_app
# from PIL import Image
# import io

# # The 'rembg' library is used for background removal
# # pip install rembg
# # If for some reason 'rembg' isn't recognized, check you have it installed in your environment
# from rembg import remove

# remove_bg_bp = Blueprint("remove_bg_bp", __name__)

# @remove_bg_bp.route("/remove_bg", methods=["POST"])
# def remove_bg():
#     """
#     Endpoint to remove the background from an image using rembg.

#     Expects:
#       - form-data with key "image" (the file)

#     Returns:
#       - A PNG with the background removed (transparent background).
#     """
#     current_app.logger.info("Remove BG endpoint hit")
#     try:
#         current_app.logger.info(f"Request content type: {request.content_type}")

#         image_file = request.files.get("image")
#         if not image_file:
#             current_app.logger.warning("No image file provided for background removal")
#             return "No image file provided", 400

#         # Open image and ensure RGBA mode for transparency
#         image = Image.open(image_file.stream).convert("RGBA")

#         current_app.logger.info("Performing background removal with rembg")
#         # Use rembg to remove the background
#         bg_removed = remove(image)

#         # Save as PNG with transparency
#         output = io.BytesIO()
#         bg_removed.save(output, format="PNG")
#         output.seek(0)

#         current_app.logger.info("Background successfully removed, sending PNG")
#         return send_file(
#             output,
#             mimetype="image/png",
#             as_attachment=True,       # triggers "download" mode in browser
#             download_name="image-no-bg.png"
#         )
#     except Exception as e:
#         current_app.logger.error(f"Error in /remove_bg: {e}")
#         return f"Remove BG error: {str(e)}", 500