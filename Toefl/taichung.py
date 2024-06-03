import contextlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_toefl_info():
    driver = webdriver.Chrome()
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
            input_box.send_keys("Taichung, 台灣")

            menu_item = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'Taichung, 台灣')]"))
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
date_info, direction_link = get_toefl_info()
if date_info and direction_link:
    print(f"最新考試日期: {date_info}\n地區位置: {direction_link}")
else:
    print("无法获取最新考试信息。")

