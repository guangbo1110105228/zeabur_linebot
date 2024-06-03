import contextlib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def get_tvn_info():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')

    chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/app/.chromedriver/bin/chromedriver')
    google_chrome_bin_path = os.getenv('GOOGLE_CHROME_BIN', '/app/.apt/usr/bin/google-chrome')

    options.binary_location = google_chrome_bin_path
    service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=options)

    driver.get('https://www.toeic.com.tw/')

    try:
        exam_date = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'selector_for_exam_date'))
        ).text
        registration_period = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'selector_for_registration_period'))
        ).text
        additional_registration_period = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'selector_for_additional_registration_period'))
        ).text
        registration_status = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'selector_for_registration_status'))
        ).text

        return {
            'exam_date': exam_date,
            'registration_period': registration_period,
            'additional_registration_period': additional_registration_period,
            'registration_status': registration_status
        }
    finally:
        driver.quit()

if __name__ == "__main__":
    info = get_tvn_info()
    if info:
        print(f"考試日期: {info['exam_date']}")
        print(f"報名期間: {info['registration_period']}")
        print(f"追加報名期間: {info['additional_registration_period']}")
        print(f"報名狀態: {info['registration_status']}")
    else:
        print("无法获取考试信息。")



