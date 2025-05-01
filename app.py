import os
import time
import base64
import threading

from flask import Flask, request, jsonify
from settings import SCRIPT_DIR
from src.image_generator import GPTImageGenerator
from src.utils import load_config, log

app = Flask(__name__)

# Load config
global config
config_path = os.path.join(SCRIPT_DIR, 'config.yaml')
config = load_config(config_path)

SECRET_TOKEN = config.get("token", [""])[0]
UPLOAD_FOLDER = config.get("uploaded_dir", ["uploads"])[0]

# Lock to ensure one request at a time
process_lock = threading.Lock()

@app.route('/trigger', methods=['POST'])
def trigger():
    # --- Auth ---
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace("Bearer ", "").strip()
    if token != SECRET_TOKEN:
        log.warning("Unauthorized request")
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # Check if busy
    if not process_lock.acquire(blocking=False):
        log.info("Server busy with another request")
        return jsonify({"status": "error", "message": "Server is busy, please try again later."}), 503

    try:
        data = request.get_json()
        if not data:
            log.error("No JSON data received")
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400

        image_b64 = data.get("image")
        prompt = data.get("prompt")
        if not image_b64:
            log.error("Image data is missing")
            return jsonify({"status": "error", "message": "No image provided"}), 400
        if not prompt:
            log.error("Prompt is missing")
            return jsonify({"status": "error", "message": "No prompt text provided"}), 400

        # Decode and save
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        image_path = os.path.join(UPLOAD_FOLDER, f"upload_{int(time.time())}.png")
        try:
            with open(image_path, 'wb') as f:
                f.write(base64.b64decode(image_b64))
            log.info(f"Image saved to {image_path}")
        except Exception as e:
            log.error(f"Failed to save image: {e}")
            return jsonify({"status": "error", "message": "Invalid image format"}), 400

        # Process image
        image, msg = run_image_generator(image_path, prompt)
        if image:
            return jsonify({"status": "success", "message": msg, "image": image}), 200
        else:
            return jsonify({"status": "error", "message": msg}), 500
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        return jsonify({"status": "error", "message": "Unexpected server error"}), 500
    finally:
        process_lock.release()


def run_image_generator(image_path, prompt):
    try:
        email = config.get("email", [""])[0]
        pwd = config.get("password", [""])[0]
        url = config.get("chatgpt_url", [""])[0]
        download_root = config.get("download_dir", ["downloads"])[0]
        download_dir = os.path.join(download_root, str(int(time.time())))
        os.makedirs(download_dir, exist_ok=True)

        log.info("Starting GPT image generator...")
        crawler = GPTImageGenerator(
            email=email,
            password=pwd,
            gpt_url=url,
            image_path=image_path,
            download_dir=download_dir,
            prompt_text=prompt
        )
        generated_img = crawler.run()
        if generated_img and os.path.exists(generated_img):
            with open(generated_img, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8'), "Image generated successfully"
        else:
            log.error("Generated image file not found")
            return None, "Generated image file not found"
    except Exception as e:
        log.error(f"Error during generation: {e}")
        return None, str(e)

if __name__ == '__main__':
    log.info("App starting...")
    app.run(host='0.0.0.0', port=80)
