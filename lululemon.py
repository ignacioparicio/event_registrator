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
import datetime

import smtplib
import imaplib
import email
from email.message import EmailMessage



def monitor(options=[]):
    """
    Monitors list of options on website (from dropdown) and triggers when a new option is added
    Args:
        options: set of initials options. A change from initial options will cause a trigger.
                 By default it fetches them from the website, but they can be passed

    Returns: Nothing, but calls an alerting function that sends email to users

    """
    # launch browser
    browser = webdriver.Chrome()
    browser.get(website)
    browser.maximize_window()

    # initialize options if not given by user
    if not options:
        options = get_options(browser)

    while True:
        new_options = get_options(browser)
        selector = new_options[2]

        # if a new option is found and it doesn't contain 'AUSVERKAUFT', alert is triggered
        for i, id in enumerate(new_options[0]):
            opt_text = new_options[1][i]
            if id not in options[0] and 'AUSVERKAUFT' not in opt_text:
                send_alert(id, opt_text, browser, selector)
        options = new_options

        # sleep and then refresh website
        snooze(1)
        browser.get(website)


def get_options(browser):
    """

    Args:
        browser: Selenium webdriver, with the target website already loaded

    Returns:
        options: list of tuples, the first tuples contains all option values and the second option text

    """
    selector = Select(browser.find_element_by_class_name("js-select-series-date"))
    option_ids = [x.get_attribute('value') for x in selector.options][1:]
    options_text = [x.text.strip() for x in selector.options][1:]
    return option_ids, options_text, selector

def snooze(mins):
    """
    'Fancy' sleep function implemented in a way compatible with keyboard interrupt
    Args:
        mins: int, minutes to sleep

    Returns: Nothing

    """
    for t in range(60 * mins):
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            continue


def send_email(email_msg):
    """
    Sends email alert with info about the new available event
    Args:
        val: string, value reference in website selector
        text: string, text of event in selector

    Returns: Nothing

    """
    msg = EmailMessage()
    msg['Subject'] = 'New ***REMOVED*** yoga class available'
    msg['From'] = 'sample_email@gmail.com'
    msg['To'] = alert_receivers

    msg.set_content(email_msg)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('sample_email@gmail.com', 'sample_pw')
        smtp.send_message(msg)


def send_alert(id, opt_text, browser, selector):
    """
    Sends email alert with info about the new available event
    Args:
        val: string, value reference in website selector
        text: string, text of event in selector

    Returns: Nothing

    """

    email_msg = f'To the attention of all ***REMOVED*** ***REMOVED***,\n\nA new ***REMOVED*** Saturday Weekly Community Class is available. It reads:\n\n{opt_text}\n\nIf you want to automatically register, answer "register" to this email.\n\nThis is an automatically generated message.'
    send_email (email_msg)
    listen(id, browser, selector)


def listen(id, browser, selector):
    timeout = time.time() + listen_time * 3600
    while True:
        if time.time() > timeout:
            send_email('Time out for registration, you can try to register manually instead')
            break

        if get_last_email().lower() == 'register':
            register(id, browser, selector)

        snooze(1)


def get_last_email():
    with imaplib.IMAP4_SSL('imap.gmail.com') as imap:
        imap.login('sample_email@gmail.com', 'sample_pw')
        imap.select("INBOX")  # imap.list() to see all folders

        # get all email ids; uses uid to search by unique id (they don't change if user deletes emails)
        status, data = imap.uid('search', None,
                                'SUBJECT "Register"')  # can use "ALL" as second argument

        return True if data else False
        #email_uids = data[0].split()

        # get latest email
        # latest_email_uid = email_uids[-1]
        # status, data = imap.uid('fetch', latest_email_uid, "(RFC822)")  # fetch the email body (RFC822) for the given ID
        # raw_email = data[0][1].decode('utf-8')
        # imap.close()

    # process email
    #email_msg = email.message_from_string(raw_email).get_payload()
    #return email_msg

def register(id, browser, selector):
    try:
        selector.select_by_value(id)

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
        # send_email('You are now registered!')
    except:
        send_email('There was an unexpected error! You can try to register manually instead')

if __name__ == "__main__":
    website = 'sample_url'
    alert_receivers = ['sample_email@outlook.com']#, 'sample_email@gmail.com']
    listen_time = 1 # time in hours

    monitor(('123', 'test')) # sample argument options: ('123', 'test')