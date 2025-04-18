import os
import yaml
import random
import time
import glob
import shutil
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from fake_useragent import UserAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)


def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        log.warning(f"Config file not found: {config_path}")
        log.info("Creating a blank config.yaml file...")
        default_yaml = """# Example 
root_paths:
  - parent path of language directory

"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(default_yaml)
        log.info("Created config.yaml. Please edit it and re-run the script.")
        exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class GPTImageGenerator:
    def __init__(self, email="", password="", gpt_url="", image_path="", prompt_text="", download_dir=""):
        self.email = email
        self.password = password
        self.gpt_url = gpt_url
        self.image_path = image_path
        self.prompt_text = prompt_text
        self.download_dir = download_dir
        self.driver = self._init_driver()

    def _init_driver(self):
        options = uc.ChromeOptions()
        ua = UserAgent()
        options.add_argument("--disable-save-password-bubble")  # This disables the save password prompt
        options.add_argument("--disable-infobars")  # Disable infobars that can show up
        options.add_argument(f"--user-agent={ua.random}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        prefs = {
            "download.prompt_for_download": False,
            "download.default_directory": os.path.abspath(self.download_dir),
            "safebrowsing.enabled": True,
            "profile.password_manager_enabled": False,  # Disable password manager
            "credentials_enable_service": False  # Disable storing credentials
        }
        options.add_experimental_option("prefs", prefs)
        return uc.Chrome(options=options)

    def _log_in(self):
        log.info("🔐 Logging in to ChatGPT...")
        self.driver.get(self.gpt_url)

        login_btn = self._wait_for_element('button[data-testid="login-button"]')
        if login_btn:
            login_btn.click()
            log.info("Clicked login button")
        else:
            log.error("Login button not found")

        email_input = self._wait_for_element("id=:r1:-email")
        if email_input:
            email_input.send_keys(self.email)
            log.info("Entered email")

        submit_button = self._wait_for_element("name=intent")
        if submit_button:
            submit_button.click()
            log.info("Clicked submit button")

        password_input = self._wait_for_element("id=:re:-password")
        if password_input:
            password_input.send_keys(self.password)
            log.info("Entered password")

        login_button = self._wait_for_element("xpath=//form[@id=':re:']/div[2]/button", by=By.XPATH)
        if login_button:
            login_button.click()
            log.info("Clicked final login button")

    def _upload_image_and_generate(self):
        log.info("📤 Uploading image...")
        # upload_button = self._wait_for_element(
        #     selector="span.flex[data-state='closed'] > button[aria-label='Upload files and more']",
        #     by=By.CSS_SELECTOR
        # )
        # if upload_button:
        #     upload_button.click()
        #
        # upload_local_file_button = self._wait_for_element(
        #     selector="//div[@role='menuitem' and contains(., 'Upload from computer')]",
        #     by=By.XPATH
        # )
        # if upload_local_file_button:
        #     upload_local_file_button.click()
        #
        # file_input = self._wait_for_element("xpath=//input[@type='file']", by=By.XPATH)
        # if file_input:
        #     file_input.send_keys(os.path.abspath(self.image_path))
        #     log.info("File uploaded via send_keys")
        # time.sleep(3)
        # prompt_input = self._wait_for_element("id=prompt-textarea")
        # if prompt_input:
        #     prompt_input.send_keys(self.prompt_text)
        #     log.info("Entered prompt text")
        self._input_text_contenteditable(self.prompt_text)

        submit_button = self._wait_for_element("id=composer-submit-button")
        if submit_button:
            submit_button.click()
            log.info("Clicked submit button")

    def _input_text_contenteditable(self, text):
        # js_script = f"""
        # var el = document.getElementById('prompt-textarea');
        # if (el) {{
        #     el.focus();
        #     el.innerHTML = '<p>{text}</p>';
        #     var event = new Event('input', {{ bubbles: true }});
        #     el.dispatchEvent(event);
        # }}
        # """
        # self.driver.execute_script(js_script)
        # Create an action chain to simulate typing
        prompt_input = self._wait_for_element("id=prompt-textarea")

        actions = ActionChains(self.driver)
        actions.move_to_element(prompt_input)
        actions.click()

        # Simulate typing (this will type one character at a time)
        actions.send_keys(text)
        actions.perform()

        log.info(f"Entered prompt text:{text}")

    def _download_image(self):
        log.info("📥 Downloading generated image...")
        created_image_text = self._wait_for_element("//span[text()='Image created']", by=By.XPATH)
        if created_image_text:
            log.info("✅ Image ready to download.")

        download_button = self._wait_for_element("//button[@aria-label='Download this image']", by=By.XPATH)
        if download_button:
            download_button.click()
            log.info("Clicked download button")
            self._wait_for_download()
            list_of_files = glob.glob(f"{self.download_dir}/*")
            latest_file = max(list_of_files, key=os.path.getctime)
            new_name = os.path.join(self.download_dir, f"{int(time.time())}.png")
            shutil.move(latest_file, new_name)
            log.info(f"✅ File downloaded and renamed to {new_name}")
        else:
            log.error("❌ Download button not found.")

    def _wait_for_download(self, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            files = glob.glob(f"{self.download_dir}/*")
            if files:
                return
            time.sleep(1)
        raise TimeoutException("File download timeout.")

    def run(self):
        try:
            self._log_in()
            self._upload_image_and_generate()
            self._download_image()
            log.info("✅ Process complete.")
        except Exception as e:
            log.exception("❌ Exception occurred during run:")
        finally:
            input("🛑 Press Enter to close browser.")
            self.driver.quit()

    def _wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=120, visible_only=False):
        try:
            if selector.startswith("id="):
                selector = selector.replace("id=", "")
                by = By.ID
            elif selector.startswith("name="):
                selector = selector.replace("name=", "")
                by = By.NAME
            elif selector.startswith("xpath="):
                selector = selector.replace("xpath=", "")
                by = By.XPATH

            time.sleep(random.uniform(1.0, 2.5))
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(
                EC.visibility_of_element_located((by, selector)) if visible_only else EC.presence_of_element_located(
                    (by, selector))
            )
            time.sleep(random.uniform(0.5, 1.0))
            return element
        except TimeoutException:
            log.warning(f"❌ Timeout: Could not find element {selector}")
            return None


if __name__ == "__main__":
    config = load_config()
    email = config.get("email", [""])[0]
    pwd = config.get("password", [""])[0]
    url = config.get("chatgpt_url", [""])[0]
    image_path = config.get("image_path", [""])[0]
    download_dir = config.get("download_dir", ["downloads"])[0]
    prompt_text = config.get("prompt_text", [""])[0]

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
