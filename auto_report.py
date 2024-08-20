from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


def auto_report(illegal_url) :
    kocsc_url = "https://www.kocsc.or.kr/main/cop/cpl/ParticipationInsertView.do"
    capture_png = './img/illegal_site' + illegal_url + ".png"

    driver.get(illegal_url)
    screenshot = driver.get_screenshot_as_png()
    with open(capture_png, 'wb') as file:
        file.write(screenshot)
    try:
        driver.get(kocsc_url)
        default_li = driver.find_element(By.ID, 'js_tab1')
        default_li.click()
        phone2_input = driver.find_element(By.ID, 'phone2')
        phone2_input.click()
        phone2_input.send_keys('1234')
        phone3_input = driver.find_element(By.ID, 'phone3')
        phone3_input.click()
        phone3_input.send_keys('5678')
        mobile2_input = driver.find_element(By.ID, 'mobile2')
        mobile2_input.click()
        mobile2_input.send_keys('1111')
        phone3_input = driver.find_element(By.ID, 'mobile3')
        phone3_input.click()
        phone3_input.send_keys('1111')
        email1_input = driver.find_element(By.ID, 'email1')
        email1_input.click()
        email1_input.send_keys('test')
        email2_input = driver.find_element(By.ID, 'email2')
        email2_input.click()
        email2_input.send_keys('naver.com')
        reply_email_checkbox = driver.find_element(By.ID, 'reply_email')
        reply_email_checkbox.click()
        reply_paper_checkbox = driver.find_element(By.ID, 'reply_paper')
        reply_paper_checkbox.click()
        detail_link = driver.find_element(By.CSS_SELECTOR, 'a.btn_t3')
        detail_link.click()
        ##################################################
        password_input = driver.find_element(By.ID, 'password')
        password_input.click()
        password_input.send_keys('httpstest')
        password_re_input = driver.find_element(By.ID, 'password_re')
        password_re_input.click()
        password_re_input.send_keys('httpstest')
        password_ca_input = driver.find_element(By.ID, 'password_ca')
        password_ca_input.click()
        password_ca_input.send_keys('red')
        driver.execute_script("document.getElementById('zip_cd1').value = '06774';")
        driver.execute_script("document.getElementById('addr1').value = '서울 서초구 강남대로 27 (양재동, AT센터)';")
        addr2_input = driver.find_element(By.ID, 'addr2')
        addr2_input.click()
        addr2_input.send_keys('4층')
        buttons = driver.find_elements(By.CLASS_NAME, "btn_t3")
        buttons[2].click()
        ################################################
        subject_input = driver.find_element(By.ID, 'subject')
        subject_input.click()
        subject_input.send_keys('불법 사이트 신고 - HTTPs')
        upload_element = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "real_upload"))
        )
        upload_element.send_keys(capture_png)
        cont_textarea = driver.find_element(By.ID, 'cont')
        cont_textarea.click()
        cont_textarea.send_keys('HTTPs Plugin을 사용한 자동 불법 사이트 신고입니다.')
        checkbox_input = driver.find_element(By.ID, 'agree')
        checkbox_input.click()
        buttons = driver.find_elements(By.CLASS_NAME, "btn_t3")
        buttons[4].click()
        ##################################################
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = Alert(driver)
        alert.accept()
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = Alert(driver)
        alert.accept()

    except:
        driver.quit()
        
auto_report('https://newtoki349.com/')