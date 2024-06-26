import contextlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time
import os

def get_toefl_info():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/app/.apt/usr/bin/google-chrome"

    chromedriver_path = "/app/.chromedriver/bin/chromedriver"
    driver = webdriver.Chrome(service=ChromeService(chromedriver_path), options=chrome_options)
    driver.get("https://v2.ereg.ets.org/ereg/public/workflowmanager/schlWorkflow?_p=TEL")

    @contextlib.contextmanager
    def suppress_errors():
        try:
            yield
        except Exception as e:
            print(f"Error occurred: {e}")

    with suppress_errors():
        try:
            button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'I Agree')]"))
            )
            button.click()
            time.sleep(2)
            
            button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Register for this test')]"))
            )
            button.click()
            time.sleep(2)
            
            input_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "location"))
            )
            input_box.send_keys("Kaohsiung City, 台灣")

            menu_item = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'Kaohsiung City, 台灣')]"))
            )
            menu_item.click()
            time.sleep(2)
            
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, 'searchResults')]"))
            )
            search_button.click()
            time.sleep(2)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'is available')]"))
            )
            
            div_element = driver.find_element(By.XPATH, "//div[contains(@aria-label, 'is available')]")
            div_element.click()
            
            date_info = div_element.get_attribute('data-sahi-date')
            test_center_element = driver.find_element(By.XPATH, "//div[contains(@class, 'testCenter-data')]")
            direction_element = test_center_element.find_element(By.XPATH, ".//li[@class='direction']//a")
            direction_link = direction_element.get_attribute("href")

            return date_info, direction_link
        
        except Exception as e:
            print(f"Error occurred: {e}")
            return None, None
        finally:
            driver.quit()

# 测试函数
if __name__ == "__main__":
    date_info, direction_link = get_toefl_info()
    if date_info and direction_link:
        print(f"最新考試日期: {date_info}\n地區位置: {direction_link}")
    else:
        print("未能獲取考試資訊。")
