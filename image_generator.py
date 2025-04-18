import os
import yaml
import random
import time
import glob
import shutil
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from icecream import ic


def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        print(f"⚠️ Config file not found: {config_path}")
        print("🔧 Creating a blank config.yaml file...")

        default_yaml = """# Example 
root_paths:
  - parent path of language directory


valid_langs:
  - EN
  - CN
  - RU

valid_types:
  - PDF
  - MP4
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(default_yaml)

        print("✅ Created config.yaml. Please edit it and re-run the script.")
        exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class GPTImageGenerator:
    def __init__(self, email="", password="", gpt_url="", image_path="", prompt_text="", download_dir=""):
        self.driver = self._init_driver()
        self.email = email
        self.password = password
        self.gpt_url = gpt_url
        self.image_path = image_path
        self.prompt_text = prompt_text
        self.download_dir = download_dir

    def _init_driver(self):
        options = uc.ChromeOptions()
        ua = UserAgent()
        options.add_argument(f"--user-agent={ua.random}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        prefs = {
            "download.prompt_for_download": False,  # No Save As dialog
            "download.default_directory": self.download_dir,  # Download folder
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        # if self.proxies:
        #     current_proxy = self.proxies[self.proxy_index % len(self.proxies)]
        #     print(f"🔌 Using proxy: {current_proxy}")
        #     options.add_argument(f'--proxy-server={current_proxy}')
        #     self.proxy_index += 1
        return uc.Chrome(options=options)

    def _log_in(self):
        try:
            self.driver.get(self.gpt_url)
            # click sign in button
            # Step 1: Find the email input and type into it
            prompt_input = self._wait_for_element("id=:r1:-email")
            if prompt_input:
                prompt_input.send_keys(self.email)
                print("📧 Typed into email input.")

            # Step 2: Click the submit button with name=intent
            submit_button = self._wait_for_element("name=intent")
            if submit_button:
                submit_button.click()
                print("✅ Clicked the intent button.")

            # Step 3: Input password
            password_input = self._wait_for_element("id=:re:-password")
            if password_input:
                password_input.send_keys("password")
                print("🔒 Password entered.")

            # Step 4: Click login button
            login_button = self._wait_for_element("xpath=//form[@id=':re:']/div[2]/button")
            if login_button:
                login_button.click()
                print("✅ Clicked login button.")

            upload_button = self._wait_for_element(
                selector="span.flex[data-state='closed'] > button[aria-label='Upload files and more']",
                by=By.CSS_SELECTOR,
                timeout=30,
                visible_only=True
            )

            if upload_button:
                try:
                    upload_button.click()
                    print("✅ Upload button clicked successfully.")
                except Exception as e:
                    print(f"❌ Failed to click upload button: {e}")
            else:
                print("❌ Upload button was not found.")

            upload_local_file_button = self._wait_for_element(
                selector="xpath=//div[@role='menuitem' and contains(., 'Upload from computer')]",
                visible_only=True
            )

            if upload_local_file_button:
                try:
                    upload_local_file_button.click()
                    print("✅ upload_local_file_button button clicked successfully.")
                except Exception as e:
                    print(f"❌ Failed to click upload button: {e}")
            else:
                print("❌ Upload button was not found.")

            # Find the hidden input and send the file path
            file_input = self._wait_for_element("xpath=//input[@type='file']")
            if file_input:
                print("file input")
                file_input.send_keys(self.image_path)  # raw string for Windows paths!
            else:
                print("can not find file input.")

            # Step : Find the email input and type into it
            prompt_input = self._wait_for_element("id=prompt-textarea")
            if prompt_input:
                prompt_input.send_keys(self.prompt_text)
                print("📧 Typed into prompt input.")

            # Step : Click the submit button with name=intent
            submit_button = self._wait_for_element("id=composer-submit-button")
            if submit_button:
                submit_button.click()
                print("✅ Clicked the submit button.")
            # Step : check created image
            created_image_text = self._wait_for_element(selector="//span[text()='Image created']", visible_only=True)
            if created_image_text:
                print("can download image:", created_image_text.text)

            # Step : Click the submit button with name=intent
            download_button = self._wait_for_element("//button[@aria-label='Download this image']")
            if download_button:
                download_button.click()
                print("✅ Clicked the download_button.")
            else:
                print("Can't download image button")

            # Wait for download to complete
            time.sleep(5)

            # Find the most recent file
            list_of_files = glob.glob(f"{self.download_dir}/*")
            latest_file = max(list_of_files, key=os.path.getctime)

            # Rename it
            new_name = os.path.join(self.download_dir, f"{time.time()}.png")
            shutil.move(latest_file, new_name)


        except Exception as e:
            ic(e)

    def run(self):
        self._log_in()
        print("🛑 Script complete. Press Enter to exit and close browser.")
        input()  # This line pauses the script
        self.driver.quit()

    def _wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=120, visible_only=False):
        try:
            # Auto-detect ID or name selectors
            if isinstance(selector, str) and selector.startswith("id="):
                selector = selector.replace("id=", "")
                by = By.ID
            elif isinstance(selector, str) and selector.startswith("name="):
                selector = selector.replace("name=", "")
                by = By.NAME
            elif isinstance(selector, str) and selector.startswith("xpath="):
                selector = selector.replace("xpath=", "")
                by = By.XPATH

            pre_sleep = random.uniform(1.0, 3.0)
            print(f"😴 Sleeping {pre_sleep:.2f}s before waiting for element...")
            time.sleep(pre_sleep)

            print(f"⏳ Waiting for element: {selector} (by={by})")
            wait = WebDriverWait(self.driver, timeout)
            if visible_only:
                element = wait.until(EC.visibility_of_element_located((by, selector)))
            else:
                element = wait.until(EC.presence_of_element_located((by, selector)))
            print("✅ Element found!")

            post_sleep = random.uniform(0.5, 1.5)
            print(f"😴 Sleeping {post_sleep:.2f}s after finding element...")
            time.sleep(post_sleep)

            return element
        except TimeoutException:
            print(f"❌ Error: Element '{selector}' was not found within {timeout} seconds.")
            return None


if __name__ == "__main__":
    config = load_config()
    email = config["email"][0]
    pwd = config["password"][0]
    url = config["chatgpt_url"][0]
    image_path = config["image_path"][0]
    download_dir = config["download_dir"][0]

    crawler = GPTImageGenerator(email=email, password=pwd, gpt_url=url, image_path=image_path,
                                download_dir=download_dir)
    crawler.run()
