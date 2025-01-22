# import io
# import base64
# from flask import Blueprint, request, jsonify, current_app
# from PIL import Image
# from rembg import remove

# remove_bg_bp = Blueprint("remove_bg_bp", __name__)

# @remove_bg_bp.route("/remove-bg", methods=["POST"])
# def remove_bg():
#     """
#     Real endpoint that uses rembg to remove backgrounds from up to 5 images.
#     Returns PNG with alpha channel in base64.
    
#     Request:
#       form-data: "images" => multiple files
#     Response:
#       {
#         "images": [
#           {
#             "filename": "...",
#             "removed_b64": "..."  # base64-encoded PNG with alpha
#           }, ...
#         ]
#       }
#     """
#     current_app.logger.info("Remove BG endpoint hit (multi-file)")

#     files = request.files.getlist("images")
#     if not files:
#         current_app.logger.warning("No images provided for remove-bg.")
#         return jsonify({"error": "No images provided"}), 400

#     if len(files) > 5:
#         current_app.logger.warning(f"Received {len(files)} images, exceeding the limit of 5.")
#         return jsonify({"error": "Max 5 images allowed"}), 400

#     results = []
#     for file in files:
#         filename = file.filename or "image.png"
#         current_app.logger.info(f"Removing BG for file: {filename}")

#         try:
#             # 1) Read raw bytes
#             input_data = file.read()
#             # 2) Pass to rembg
#             out_data = remove(input_data)
#             # 3) Convert result bytes to a Pillow image (RGBA)
#             out_img = Image.open(io.BytesIO(out_data)).convert("RGBA")

#             # 4) Save it to PNG in memory
#             output = io.BytesIO()
#             out_img.save(output, format="PNG")
#             output.seek(0)

#             # 5) Convert to base64
#             b64_data = base64.b64encode(output.getvalue()).decode("utf-8")
#             results.append({
#                 "filename": filename,
#                 "removed_b64": b64_data
#             })
#         except Exception as e:
#             current_app.logger.error(f"Failed to remove BG for {filename}: {e}")
#             results.append({
#                 "filename": filename,
#                 "error": str(e),
#                 "removed_b64": None
#             })

#     return jsonify({"images": results})
