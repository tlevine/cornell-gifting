#!/usr/bin/env python2
"Donate lots of small amounts to Cornell."

from requests import session
from lxml.html import fromstring
from json import loads

s = session()

honoree = {
    'gift_amount': '0.01',
    'designation': '22',
    'designation2': 'Cornell University 001004',
    'designation_other': '',
    'iho_imo': 'iho',
    'h_type': 'person',
    'honoree': 'Raskolnikov',
    'notify_name': 'Raskolnikov',
    'notify_address': '122 Risley Hall',
    'notify_address2': '',
    'notify_city': 'Ithaca',
    'notify_state': 'NY',
    'notify_zip': '14853',
    'notify_country': 'US',
    'notify_comments': '',
    'gift_type': 'gift1',
    'end_year': '2013',
    'step': '1',
}

personal = {
    'title': 'Mr',
    'fname': 'Thomas',
    'mname': 'Kai',
    'lname': 'Levine',
    'name_oncard': 'Thomas Levine',
    'empid': '',
    'classyear': '',
    'spousename': '',
    'spouseyear': '',
    'matchcomp': '',
    'address': '54 Walworth Avenue',
    'address2': '',
    'city': 'Scarsdale',
    'state': 'NY',
    'province': '',
    'postal_code': '10583-1423',
    'country': 'US',
    'email': '',
    'email_type': 'personal',
    'phone': '607-699-1866',
    'phone_type': 'personal',
    'step': '2',
}

payment_base = {
    'subaction': '',
    'startdate_month': '',
    'startdate_year': '',
    'issue_number': '',
    'METHOD': 'C',
    'PAYMETHOD': 'C',
    'FIRST_NAME': 'Thomas',
    'LAST_NAME': 'Levine',
    'template': '',
    'ADDRESS': '54 Walworth Avenue',
    'CITY': 'Scarsdale',
    'STATE': 'NY',
    'ZIP': '105831423',
    'COUNTRY': 'US',
    'PHONE': '607-699-1866',
    'EMAIL': 'perluette@thomaslevine.com',
    'SHIPPING_FIRST_NAME': '',
    'SHIPPING_LAST_NAME': '',
    'ADDRESSTOSHIP': '',
    'CITYTOSHIP': '',
    'STATETOSHIP': '',
    'ZIPTOSHIP': '',
    'COUNTRYTOSHIP': 'US',
    'PHONETOSHIP': '',
    'EMAILTOSHIP': '',
    'TYPE': 'S',
    'SHIPAMOUNT': '0.00',
    'TAX': '0.00',
    'VERBOSITY': 'HIGH',
    'PONUM': '10583-1423',
    'flag3dSecure': '',
    'swipeData': '0',
    'SECURETOKEN': None,
    'SECURETOKENID': None,
    'PARMLIST': '',
    'MODE': 'live',
    'referringTemplate': 'minlayout',
    'pay.x': 'Pay Now',
}

credit_card = loads(open('creditcard.json').read())

# Go to the first page
r = s.get('http://www.alumni.cornell.edu/seniorclass/give/')

# Choose credit card
r = s.post('http://www.alumni.cornell.edu/seniorclass/give/cfxcgi/redirect.cfm', {'type': 'giving_cc'})
r = s.get(r.headers['location'])

# Step 1
r = s.post('https://www.giving.cornell.edu/give/index.cfm', honoree)

# Step 2
r = s.post('https://www.giving.cornell.edu/give/index.cfm', {'continue': 'true', 'step': '1'})
r = s.post('https://www.giving.cornell.edu/give/index.cfm', personal)

# Payment form
r = s.get('https://www.giving.cornell.edu/give/' + fromstring(r.text).xpath('//iframe/@src')[0])
html = fromstring(r.text)
params = {input.attrib['name']: input.attrib['value'] for input in html.xpath('//form/input')}
r = s.post(html.xpath('//form/@action')[0], params)

# Pay
payment = payment_base
payment.update(credit_card)
html = fromstring(r.text)
for securetoken in ['SECURETOKEN', 'SECURETOKENID']:
    values = html.xpath('//input[@name="%s"]/@value' % securetoken)
    if len(values) == 1:
        payment[securetoken] = values[0]
    else:
        raise ValueError(
            'There should be exactly one %s, but there are %d.' %
            (securetoken, len(values))
        )

r = s.post('https://payflowlink.paypal.com/processTransaction.do', payment)
print r.text
