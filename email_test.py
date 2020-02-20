"""
Created on 20/02/2020 14:52

@author: Ignacio Paricio
"""

import smtplib

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    # identify ourselves, likely redundant
    smtp.ehlo()
    # activate encryption
    smtp.starttls()
    # re-identify ourselves after securing connection
    smtp.ehlo()

    smtp.login('sample_email@gmail.com', 'sample_pw')

    subject = 'New session!'
    body = 'A new class opened'
    msg = f'Subject: {subject}\n\n{body}'

    smtp.sendmail('sample_email@gmail.com', 'ignacio.outlook@outlook.com', msg)
    print('email sent')