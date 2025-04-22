import os
import yaml
import logging
import colorlog

from settings import SCRIPT_DIR

# Create logs directory if it doesn't exist
log_path = os.path.join(SCRIPT_DIR, "logs")
os.makedirs(log_path, exist_ok=True)

# Create formatter for file logs (no color)
file_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
)
# Create file handler
file_handler = logging.FileHandler(log_path + "/app.log")
file_handler.setFormatter(file_formatter)

# Create color formatter for console
color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

# Create console handler
console_handler = colorlog.StreamHandler()
console_handler.setFormatter(color_formatter)

# Setup logger
log = colorlog.getLogger("colored_logger")
log.setLevel(logging.DEBUG)
log.addHandler(console_handler)
log.addHandler(file_handler)


def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        log.warning(f"Config file not found: {config_path}")
        log.info("Creating a blank config.yaml file...")
        default_yaml = """# Example 
email:
  - GPT user email
password:
  - GPT user password
chatgpt_url:
  - https://chatgpt.com/
image_path:
  - local test image path
prompt_text:
  - test prompt
download_dir:
  - generated image is downloaded in this directory
token:
  - test_token
uploaded_dir:
  - requesting image is saved in this directory

"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(default_yaml)
        log.warning("Created config.yaml. Please edit it and re-run the script.")
        exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
