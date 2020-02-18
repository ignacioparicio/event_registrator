"""
Created on 17/02/2020 20:29

@author: Ignacio Paricio
"""

from selenium import webdriver
from pathlib import Path
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
browser = webdriver.Chrome()

#html_file = Path.cwd() / "can_register.html"
#browser.get(html_file.as_uri())
browser.get('sample_url')
browser.maximize_window()

def get_options():
    selector = Select(browser.find_element_by_class_name("js-select-series-date"))
    option_vals = [x.get_attribute('value') for x in selector.options][1:]
    options_text = [x.text for x in selector.options][1:]
    options = dict(zip(range(len(option_vals)), zip(option_vals, options_text)))
    return options, selector


def register(id, options):
    selector.select_by_value(options[id][0])

    # wait for next element given dropdown change drives page update
    checkout = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'js-checkout-button')))
    checkout.click()

    # wait for page
    first_name = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.ID, 'first_name')))
    first_name.send_keys('FirstName')
    last_name = browser.find_element_by_id('last_name')
    last_name.send_keys('LastName')
    email = browser.find_element_by_id('email_address')
    email.send_keys('sample_email@gmail.com')
    email2 = browser.find_element_by_id('confirm_email_address')
    email2.send_keys('sample_email@gmail.com')

    # finish registration
    # browser.find_element_by_link_text("Registrierung abschließen").click()

options, selector = get_options()
id = 1
register(id, options)



def monitor(options):
    while True:
        # 'fancy' sleep so that it can be interrupted
        for t in range(60 * 30):
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                continue
        browser.get('sample_url')

        # fix so that only options with new value trigger
        new_options, selector = get_options()
        for option in last:
            if option not in current:
                print("New option!")