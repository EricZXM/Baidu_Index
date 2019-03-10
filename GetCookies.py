import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from setting import ChromePath, Baidu_User_ID, Baidu_Password

browser = webdriver.Chrome(ChromePath)
browser.get("https://index.baidu.com/#/")
time.sleep(5)
login = browser.find_element_by_class_name('links-item-unlogin')
login.click()
wait = WebDriverWait(browser, 30)
wait.until(EC.presence_of_element_located((By.ID, 'TANGRAM__PSP_4__userName')))
input_name = browser.find_element_by_id('TANGRAM__PSP_4__userName')
input_name.send_keys(Baidu_User_ID)
input_password = browser.find_element_by_id('TANGRAM__PSP_4__password')
input_password.send_keys(Baidu_Password)

time.sleep(15)
submit = browser.find_element_by_id('TANGRAM__PSP_4__submit')
submit.click()

cookies = browser.get_cookies()
browser.close()


file = open("cookies.txt", "w")
for c in cookies:
    file.write(str(c))
    file.write("\n")

file.close()