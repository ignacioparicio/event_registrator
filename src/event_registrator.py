"""
Created on 17/02/2020 20:29

@author: Ignacio Paricio
"""
import time
import datetime
import smtplib
import imaplib
import email
from email.message import EmailMessage
import yaml
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# TODO: Implement as a class 'EventRegistrator'
# TODO: Figure out how to run from EC2 instance


def snooze(secs: int):
    """Fancy sleep function with keyboard interrupt support."""
    for _ in range(round(secs)):
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            continue


def send_email(email_msg: str):
    """Sends email alert with info about the new available event."""
    msg = EmailMessage()
    msg["Subject"] = config["email"]["subject"]
    msg["From"] = config["email"]["sender"]
    msg["To"] = config["email"]["alert_receivers"]

    msg.set_content(email_msg)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(config["email"]["sender"], config["email"]["password"])
        smtp.send_message(msg)


def get_last_email():
    """Gets last email from inbox."""
    with imaplib.IMAP4_SSL("imap.gmail.com") as imap:
        imap.login(config["email"]["sender"], config["email"]["password"])
        imap.select("INBOX")  # If in doubt,use imap.list() to see all folders

        # Get all emails unique ids
        _, data = imap.uid("search", None, "ALL")
        email_uids = data[0].split()

        # Fetch the email body (RFC822) for last unique id (last received email)
        _, data = imap.uid("fetch", email_uids[-1], "(RFC822)")
        raw_email = data[0][1].decode("utf-8")
        imap.close()

        # TODO: Using snippet below for inspiration on how to use a tag to search for
        #  specific emails instead of reading just the last email
        # status, data = imap.uid('search', None, 'SUBJECT "silence"')
        # for id in email_uids:
        #     status, data = imap.uid('fetch', id, "(RFC822)")
        #     raw_email = data[0][1].decode('utf-8')
        #     email_msg = email.message_from_string(raw_email)
        #     email_subject = email_msg['Subject']
        #     print(email_subject)

    email_msg = email.message_from_string(raw_email)
    return email_msg


def get_options():
    """Returns classes available from dropdown selector."""
    global SELECTOR
    element = WebDriverWait(BROWSER, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "js-select-series-date"))
    )
    SELECTOR = Select(element)
    option_ids = [x.get_attribute("value") for x in SELECTOR.options][1:]
    options_text = [x.text.strip() for x in SELECTOR.options][1:]
    return option_ids, options_text


def load_website():
    """Navigates javascript interface from parent website to list of classes."""
    BROWSER.get(config["website"])
    sat_class = BROWSER.find_elements_by_xpath(
        "//*[contains(text(), 'Weekly Community Class on Saturday')]"
    )
    sat_class[0].click()


def monitor():
    """Monitors list of classes and triggers alert when a new option is added."""
    print(f"{datetime.datetime.now()} - Launching web driver")
    global BROWSER, ID, OPT_TEXT  # TODO: get rid of this, implement as class
    BROWSER = webdriver.Chrome()
    BROWSER.maximize_window()
    load_website()

    options = ([None], [None])
    while True:
        print(f"{datetime.datetime.now()} - Monitoring...")
        new_options = get_options()

        # Trigger email alert if a new option is found and isn't 'AUSVERKAUFT'
        for i, ID in enumerate(new_options[0]):
            OPT_TEXT = new_options[1][i]
            if ID not in options[0] and "AUSVERKAUFT" not in OPT_TEXT:
                print(f"{datetime.datetime.now()} - New valid option found")
                send_alert()
        options = new_options

        # Refresh website according to specified frequency
        snooze(config["frequencies"]["monitor_freq"] * 3600)
        load_website()


def send_alert():
    """Sends email alert with info about the new available class."""
    email_msg = (
        config["email"]["body_register_intro"]
        + f"\n\nNew class: {OPT_TEXT}\n\n"
        + config["email"]["body_register_how_to"]
        + config["email"]["auto_msg_flag"]
    )
    send_email(email_msg)
    print(f"{datetime.datetime.now()} - Alert sent")
    listen()


def listen():
    """Monitors email inbox for an answer to trigger registration."""
    timeout = time.time() + config["frequencies"]["listen_timeout"] * 3600
    print(f"{datetime.datetime.now()} - Listening...")
    while True:
        snooze(config["frequencies"]["listen_freq"])
        if time.time() > timeout:
            send_email(
                config["email"]["body_timeout"] + config["email"]["auto_msg_flag"]
            )
            print(f"{datetime.datetime.now()} - Listening timed out")
            break
        # TODO: think of a more robust alternative
        if get_last_email()["Subject"].lower() == "register":
            register()
            break


def register():
    """Registers user for an event."""
    try:
        print(
            f"{datetime.datetime.now()} - Confirmation to register received, trying to register"
        )
        SELECTOR.select_by_value(ID)

        # Wait for next element given dropdown change drives page update
        checkout = WebDriverWait(BROWSER, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "js-checkout-button"))
        )
        checkout.click()

        first_name_box = WebDriverWait(BROWSER, 60).until(
            EC.presence_of_element_located((By.ID, "first_name"))
        )
        first_name_box.send_keys(config["registree"]["first_name"])
        last_name_box = BROWSER.find_element_by_id("last_name")
        last_name_box.send_keys(config["registree"]["last_name"])
        email_box = BROWSER.find_element_by_id("email_address")
        email_box.send_keys(config["registree"]["email_address"])
        email2_box = BROWSER.find_element_by_id("confirm_email_address")
        email2_box.send_keys(config["registree"]["email_address"])

        if config["enable_registration"]:
            BROWSER.find_element_by_link_text("Registrierung abschließen").click()

        send_email(
            "You are now registered for the following class:\n\n"
            + OPT_TEXT
            + "\n\n"
            + config["email"]["auto_msg_flag"]
        )
        print(
            f"{datetime.datetime.now()} - Registration successful! Confirmation email sent"
        )
    except:  # TODO: fix bare-except
        send_email(config["registree"]["email_address"] + config["email"]["body_error"])


if __name__ == "__main__":
    with open(r"config.yaml") as file:  # Load configuration
        config = yaml.full_load(file)
    monitor()
