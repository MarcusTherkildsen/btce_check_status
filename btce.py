# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 22:35:52 2015
@author: Marcus Therkildsen
"""
import httplib
import urllib
import json
import hashlib
import hmac
from time import sleep


def contact_btce(key, secret, nonce):

    # Method name and nonce go into the POST parameters
    params = {"method": "getInfo",
              "nonce": nonce}
    params = urllib.urlencode(params)

    # Hash the params string to produce the Sign header value
    H = hmac.new(BTC_api_secret, digestmod=hashlib.sha512)
    H.update(params)
    sign = H.hexdigest()

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Key": BTC_api_key,
               "Sign": sign}
			   
	# Connect to BTC-e and get response
    conn = httplib.HTTPSConnection("btc-e.com")
    conn.request("POST", "/tapi", params, headers)
    response = json.load(conn.getresponse())

    # Check if connection to BTC-e and if nonce was succesfull
    if 'error' in response:
        if 'invalid nonce parameter;' in response['error']:
            open_orders = -1

            # Get the proper nonce
            l = []
            for t in str(response['error']).replace(":", " ").split():
                try:
                    l.append(float(t))
                except ValueError:
                    pass
    else:
        open_orders = response['return']['open_orders']
        l = [-1]

    conn.close()

    return open_orders, int(l[0])


def send_mail(message):

    import smtplib

    # Sender and receiver
    s = 'Sender email'
    s_pass = 'Sender email password'
    r = 'Receiver email address'

    # Email server and port
    mail = smtplib.SMTP('email server', 'port')
    mail.ehlo()
    mail.starttls()
    mail.login(s, s_pass)

    # Header needed
    header = 'To:' + r + '\n' + 'From: ' + s + '\n' + 'Subject:BTC-e order \n'
    content = header + '\n ' + message + ' \n\n'
    mail.sendmail(s, r, content)
    mail.close()

if __name__ == '__main__':

    # Replace these with your own API key data
    BTC_api_key = "Your api key"
    BTC_api_secret = "Your api secret"

    nonce = 0
    check = 1
    while check == 1:
        # Check status of btc-e
        open_orders, nonce = contact_btce(BTC_api_key, BTC_api_secret, nonce)
        sleep(1)

        if open_orders == 0 and nonce == -1:
            # print 'No open orders, time to send an email'
            # send_mail('No open orders, login and check status: https://btc-e.com/')
            break

        elif open_orders > 0 and nonce == -1:
            # print 'Order still going, do nothing'
            # send_mail('Order still active: https://btc-e.com/')
            break
