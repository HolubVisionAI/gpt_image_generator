# GPT Image Generator

A Flask-based API that accepts a base64 image and prompt, then uses a headless browser to interact with the GPT-based image generation UI. The generated image is returned in base64 format.

## 📦 Environment Setup

### 🐍 Python Version
This project uses **Python 3.10**

### 🔧 Setup Virtual Environment

```bash
python -m venv venv10
source venv10/bin/activate   # On Windows use: venv10\Scripts\activate
```

### 📦 Install Requirements

```bash
pip install -r ./requirements/base.txt
```

### 🌐 Install Google Chrome

Required for running the image generator that uses headless browser automation.

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

---

## ⚙️ Configuration

Edit the `config.yaml` file in the root directory:

```yaml
token:
  - "your-secret-token"

email:
  - "your-gpt-email@example.com"

password:
  - "your-gpt-password"

chatgpt_url:
  - "https://chat.openai.com"

uploaded_dir:
  - "uploads"

download_dir:
  - "downloads"
```

---

## 🚀 Run the API Server

```bash
python main.py
```

Server will start on `http://0.0.0.0:5000`

---

## 📡 API Endpoint

### `POST /trigger`

Trigger the image generation process.

#### 🔐 Headers

- `Authorization: Bearer <your-secret-token>`

#### 📤 Request JSON

```json
{
  "image": "<base64-encoded-image>",
  "prompt": "Describe what to generate"
}
```

#### 📥 Response (Success)

```json
{
  "status": "success",
  "message": "Image is generated from GPT UI",
  "image": "<base64-encoded-generated-image>"
}
```

#### ❌ Response (Errors)

- 401 Unauthorized — Invalid token
- 400 Bad Request — Missing prompt or image
- 500 Server Error — Internal failure during generation

---

## 📁 Project Structure

```
.
├── main.py                  # Flask API entry point
├── settings.py              # Defines SCRIPT_DIR
├── config.yaml              # Config file for credentials and directories
├── requirements/
│   └── base.txt             # Python dependencies
├── src/
│   ├── image_generator.py   # GPTImageGenerator class (browser-based)
│   └── utils.py             # Utility functions (logging, config loading)
├── uploads/                 # Uploaded images (created at runtime)
├── downloads/               # Generated images (created at runtime)
```

---

## 🧠 GPT Image Generation

The image generation works by automating browser actions to interact with the ChatGPT image generation UI using the credentials provided in `config.yaml`.

---

Let me know if you’d like a markdown version saved or want to add diagrams or usage examples!