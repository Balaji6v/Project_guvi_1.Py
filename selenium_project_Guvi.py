import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def is_visible(self, by, locator):
        try:
            element = self.wait.until(EC.visibility_of_element_located((by, locator)))
            logging.info(f"Element visible: {locator}")
            return True
        except TimeoutException:
            logging.warning(f"Element NOT visible: {locator}")
            return False

    def click_element(self, by, locator):
        try:
            element = self.wait.until(EC.element_to_be_clickable((by, locator)))
            element.click()
            logging.info(f"Clicked on: {locator}")
        except (TimeoutException, ElementNotInteractableException) as e:
            logging.error(f"Error clicking {locator}: {e}")
            raise

    def input_text(self, by, locator, text):
        try:
            field = self.wait.until(EC.presence_of_element_located((by, locator)))
            field.clear()
            field.send_keys(text)
            logging.info(f"Input text in: {locator}")
        except TimeoutException as e:
            logging.error(f"Error inputting text in {locator}: {e}")
            raise

    def get_text(self, by, locator):
        try:
            return self.wait.until(EC.visibility_of_element_located((by, locator))).text
        except TimeoutException:
            return ""


class HomePage(BasePage):
    def go_to_signup(self):
        return self.click_element(By.XPATH, "//a[contains(text(),'Sign up')]")

    def go_to_login(self):
        return self.click_element(By.XPATH, "//a[contains(text(),'Login')]")

    def is_login_visible(self):
        return self.is_visible(By.XPATH, "//a[contains(text(),'Login')]")

    def is_signup_visible(self):
        return self.is_visible(By.XPATH, "//a[contains(text(),'Sign up')]")


class LoginPage(BasePage):
    def login(self, email, password):
        self.input_text(By.XPATH, "//input[@type='email']", email)
        self.input_text(By.XPATH, "//input[@type='password']", password)
        self.click_element(By.XPATH, "//button[@type='submit']")

    def get_error_message(self):
        return self.get_text(By.CLASS_NAME, "error-msg")  # Adjust locator based on actual error


class DashboardPage(BasePage):
    def logout(self):
        self.click_element(By.XPATH, "//button[@aria-label='profile']")
        self.click_element(By.XPATH, "//button[contains(text(),'Logout')]")


def test_guvi_webcode_suite():
    logging.basicConfig(level=logging.INFO)
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    url = "https://www.guvi.in/"
    login_url = "https://www.guvi.in/sign-in"
    expected_title = "GUVI | Learn to code in your native language"
    dashboard_url = "https://www.guvi.in/dashboard"
    signup_url = "https://www.guvi.in/register/"
    valid_email = "balajivenkat132002@gmail.com"
    valid_password = "Balaji@13"
    invalid_email = "invalid@guvi.in"
    invalid_password = "WrongPass123"

    try:
        driver.get(url)

        # Test Case 1: URL check
        assert "guvi.in" in driver.current_url

        # Test Case 2: Title check
        assert expected_title in driver.title

        homepage = HomePage(driver)

        # Test Case 3: Login button visible & clickable
        assert homepage.is_login_visible()
        homepage.go_to_login()

        # Test Case 5: Check if login page opens
        WebDriverWait(driver, 10).until(EC.url_to_be(login_url))
        assert driver.current_url == login_url

        login_page = LoginPage(driver)

        # Test Case 4: Sign-up button visible & clickable (go back to home)
        driver.get(url)
        assert homepage.is_signup_visible()
        homepage.go_to_signup()
        WebDriverWait(driver, 10).until(EC.url_to_be(signup_url))
        assert driver.current_url == signup_url

        # Test Case 6: Valid login and logout
        driver.get(login_url)
        login_page.login(valid_email, valid_password)
        WebDriverWait(driver, 10).until(EC.url_to_be(dashboard_url))
        assert driver.current_url == dashboard_url
        dashboard = DashboardPage(driver)
        dashboard.logout()
        WebDriverWait(driver, 10).until(EC.url_contains("sign-in"))

        # Test Case 7: Invalid login
        driver.get(login_url)
        login_page.login(invalid_email, invalid_password)
        error_msg = login_page.get_error_message()
        assert error_msg != "", "Expected an error message for invalid login"

        logging.info(" All test cases passed.")

    except AssertionError as ae:
        logging.error(f" Assertion failed: {ae}")
    except Exception as e:
        logging.error(f" Test failed with exception: {e}")
    finally:
        driver.quit()
        logging.info("🧹 Browser closed.")


if __name__ == "__main__":
    test_guvi_webcode_suite()
