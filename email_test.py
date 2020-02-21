"""
Created on 20/02/2020 14:52

@author: Ignacio Paricio
"""

import smtplib
import imaplib
import email
import datetime
from email.message import EmailMessage

# # send email
# msg = EmailMessage()
# msg['Subject'] = 'New ***REMOVED*** yoga class available'
# msg['From'] = 'sample_email@gmail.com'
# msg['To'] = ['sample_email@outlook.com', 'sample_email@gmail.com']
# msg.set_content('New options available...')
#
# with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#     smtp.login('sample_email@gmail.com', 'sample_pw')
#     smtp.send_message(msg)
#     print('email sent')

# monitor emails https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
with imaplib.IMAP4_SSL('imap.gmail.com') as imap:
    imap.login('sample_email@gmail.com', 'sample_pw')
    imap.select("INBOX") # imap.list() to see all folders

    # get all email ids; uses uid to search by unique id (they don't change if user deletes emails)
    status, data = imap.uid('search', None, 'SUBJECT "Register"') # can use "ALL" as second argument
    email_uids = data[0].split()

    # get latest email
    latest_email_uid = email_uids[-1]
    status, data = imap.uid('fetch', latest_email_uid, "(RFC822)") # fetch the email body (RFC822) for the given ID
    raw_email = data[0][1].decode('utf-8')
    
    imap.close()

# process email
email_msg = email.message_from_string(raw_email)
choice = email_msg.get_payload()
print(choice)


# check messages altenative https://www.youtube.com/watch?v=njDGaVnz9Z8
# yet another alternative https://gist.github.com/jonathanhculver/4281908
# alternative with Google API https://developers.google.com/gmail/api/quickstart/python