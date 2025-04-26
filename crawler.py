from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from constants import *

def SeleniumGetHTML(url, headless=True):
  options = Options()
  if headless:
      options.add_argument("--headless")
  driver = webdriver.Firefox(options=options)
  driver.get(url)
  try:
    element = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CLASS_NAME, CONTAINER_CLASS))
    )
  finally:
    tmp = driver.page_source
    driver.close()
    return tmp