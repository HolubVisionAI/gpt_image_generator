import os
import time
import traceback

from flask import Flask, request, jsonify
# from selenium_script import run_selenium
import base64

from settings import SCRIPT_DIR
from src.image_generator import GPTImageGenerator
from src.utils import load_config

app = Flask(__name__)

config_path = os.path.join(SCRIPT_DIR, 'config.yaml')
config = load_config(config_path)
SECRET_TOKEN = config.get("token", [""])[0]
UPLOAD_FOLDER = config.get("uploaded_dir", [""])[0]


@app.route('/trigger', methods=['POST'])
def trigger():
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace("Bearer ", "")

    if token != SECRET_TOKEN:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"status": "error", "message": "No image provided"}), 400
    if not data or 'prompt' not in data:
        return jsonify({"status": "error", "message": "No prompt text provided"}), 400

    try:
        image_data = base64.b64decode(data['image'])
        prompt = data['prompt']
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        image_path = os.path.join(UPLOAD_FOLDER, f"upload_{int(time.time())}.png")
        with open(image_path, "wb") as f:
            f.write(image_data)
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid image format"}), 400
    print(image_path)
    # result = run_selenium(image_path)
    if image_path and prompt:
        image, msg = run_image_generator(image_path, prompt)
        return jsonify({"status": "success", "message": msg, "image": image})
    return jsonify({"status": "error", "message": "Invalid prompt or image"})


def run_image_generator(image_path, prompt):
    try:
        email = config.get("email", [""])[0]
        pwd = config.get("password", [""])[0]
        url = config.get("chatgpt_url", [""])[0]
        download_dir = config.get("download_dir", ["downloads"])[0]

        if not all([email, pwd, url]):
            raise ValueError("Missing email, password, or chatgpt_url in config")

        prompt_text = prompt
        image_path = image_path

        os.makedirs(download_dir, exist_ok=True)

        crawler = GPTImageGenerator(
            email=email,
            password=pwd,
            gpt_url=url,
            image_path=image_path,
            download_dir=download_dir,
            prompt_text=prompt_text
        )

        generated_img = crawler.run()

        if generated_img and os.path.exists(generated_img):
            with open(generated_img, "rb") as img_file:
                encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
                return encoded_image, "image is generated from GPT UI"
        else:
            raise FileNotFoundError("Generated image not found or invalid path")


    except Exception as e:
        print("Error during image generation:", str(e))
        traceback.print_exc()  # Optional: shows full traceback
        return None, str(e)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
