"""
Created on 17/02/2020 20:29

@author: Ignacio Paricio
"""

from selenium import webdriver
from pathlib import Path
import time
browser = webdriver.Chrome()

html_file = Path.cwd() / "can_register.html"
browser.get(html_file.as_uri())
#browser.get('sample_url')

def get_options():
    element = browser.find_element_by_class_name('js-select-series-date')
    options = [x.text.strip() for x in element.find_elements_by_tag_name("option")]
    return options[1:] # filter out first option given it is default text

current = get_options()
while True:
    last = get_options()
    for option in last:
        if option not in current:
            print("New option!")

    print("Now sleeping for 30min...")
    # 'fancy' sleep so that it can be interrupted
    for t in range(60 * 30):
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            continue
    browser.refresh()

# find button and do btn.click()
# name = browser.find_element_by_id(...)
# name.send_keys('Ignacio')