import os
import time
from src.image_generator import GPTImageGenerator
from src.utils import load_config

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.yaml')
    config = load_config(config_path)
    email = config.get("email", [""])[0]
    pwd = config.get("password", [""])[0]
    url = config.get("chatgpt_url", [""])[0]
    image_path = config.get("image_path", [""])[0]
    download_dir = config.get("download_dir", ["downloads"])[0]
    prompt_text = config.get("prompt_text", [""])[0]
    # download_dir = os.path.join(download_dir, str(int(time.time())))

    os.makedirs(download_dir, exist_ok=True)

    crawler = GPTImageGenerator(
        email=email,
        password=pwd,
        gpt_url=url,
        image_path=image_path,
        download_dir=download_dir,
        prompt_text=prompt_text
    )
    crawler.run()
