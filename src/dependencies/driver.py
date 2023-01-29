from selenium import webdriver

def get_driver():
    # setting webdriver selenium -- aviod bot detected
    option = webdriver.ChromeOptions()
    # Removes navigator.webdriver flagIngest
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option('useAutomationExtension', False)
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument("--incognito")
    option.add_argument('disable-notifications')
    option.add_argument('--disable-infobars')
    option.add_argument('start-maximized')
    # To disable the message, "Chrome is being controlled by automated test software"
    option.add_argument("disable-infobars")
    option.add_argument('--disable-blink-features=AutomationControlled')
    option.add_argument("window-size=1280,800")
    
    return webdriver.Chrome(executable_path='../chromedriver.exe', options=option)

