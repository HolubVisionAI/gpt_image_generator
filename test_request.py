import os

import requests
import base64

from settings import SCRIPT_DIR
from src.utils import load_config

config_path = os.path.join(SCRIPT_DIR, 'config.yaml')
config = load_config(config_path)
token = config.get("token", [""])[0]
prompt = config.get("prompt_text", [""])[0]

# Load a test image and encode in base64
with open("tests/sample.png", "rb") as img_file:
    encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "image": encoded_image,
    "prompt": prompt
}

response = requests.post("http://localhost:5000/trigger", json=data, headers=headers)
print(response.json())
