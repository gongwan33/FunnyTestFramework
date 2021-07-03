from selenium.webdriver.common.by import By

def ExampleCustomStep(driver, testParam):
    
    try:
        driver.get("https://github.com")

        img = driver.find_element(By.CSS_SELECTOR, 'img')

        return img.get_attribute('src') == 'testParam1'
    except Exception as e:

        print(e)
        return False