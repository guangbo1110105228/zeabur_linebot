import contextlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_chw_info():
    options = webdriver.ChromeOptions()
    options.binary_location = "/app/.apt/usr/bin/google-chrome"
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(executable_path='/app/.chromedriver/bin/chromedriver', options=options)
    driver.get("https://www.toeic.com.tw/toeic/listening-reading/registration/test-dates/")

    @contextlib.contextmanager
    def GetTopic():
        try:
            yield
            tool_item = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='tool-item']"))
            )
            checkbox = tool_item.find_element(By.XPATH, "//input[@data-country='中彰投']")
            driver.execute_script("arguments[0].click();", checkbox)
            time.sleep(2)

            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn--serch js-search gtm-test-search']"))
            )
            search_button.click()

            tables = WebDriverWait(driver, 10).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.table-data-accordion'))
            )

            def process_table(table):
                try:
                    exam_date_cell = table.find_element(By.XPATH, ".//td[@data-title='測驗日期']")
                    date_info_element = exam_date_cell.find_element(By.XPATH, ".//div[@class='flex margin-r-11']")
                    date_elements = date_info_element.find_elements(By.TAG_NAME, 'span')
                    month = date_elements[0].text.strip()
                    day = date_elements[2].text.strip()
                    exam_date = f"{month}/{day}"

                    registration_cell = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, "//td[@data-title='報名期間'][1]"))
                    )
                    date_spans = registration_cell.find_elements(By.TAG_NAME, 'span')
                    registration_period = ' '.join(span.text.strip() for span in date_spans[:3])

                    try:
                        additional_registration_cell = registration_cell.find_element(By.XPATH, ".//div[@data-title='追加報名期間']")
                        additional_date_spans = additional_registration_cell.find_elements(By.TAG_NAME, 'span')
                        additional_registration_period = ' '.join(span.text.strip() for span in additional_date_spans[:3])
                    except Exception:
                        additional_registration_period = "無追加報名期間"

                    online_registration_cell = table.find_element(By.XPATH, ".//td[@data-title='線上報名']")
                    registration_status_elements = online_registration_cell.find_elements(By.XPATH, ".//p[@class='table-status']")
                    if registration_status_elements:
                        registration_status = "報名截止"
                        return {
                            'exam_date': exam_date,
                            'registration_period': registration_period,
                            'additional_registration_period': additional_registration_period,
                            'registration_status': registration_status
                        }
                    else:
                        registration_link = online_registration_cell.find_element(By.TAG_NAME, 'a')
                        registration_url = registration_link.get_attribute("href")
                        return {
                            'exam_date': exam_date,
                            'registration_period': registration_period,
                            'additional_registration_period': additional_registration_period,
                            'registration_status': f"線上報名連結: {registration_url}"
                        }
                except Exception as e:
                    return None

            for table in tables:
                info = process_table(table)
                if info:
                    return info
            return None

        except Exception as e:
            return None

        finally:
            driver.quit()

    with GetTopic():
        pass



