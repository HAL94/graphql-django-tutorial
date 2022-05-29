from twilio.rest import Client
import pyotp
from core.settings import TWILIO

def send_twilio_otp(mobile_number):
    account_sid = TWILIO['ACCOUNT_SID']
    auth_token = TWILIO['AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    otp_fact = pyotp.TOTP('base32secret3232')
    otp = otp_fact.now() 
    body = f'Welcome to Big Bag, to complete your registeration, enter the OTP: {otp}'

    message = client.messages.create(  
        messaging_service_sid=TWILIO['MESSAGING_SERVICE_SID'],
        to=mobile_number,
        body=body
    ) 
    
    print(message.sid)    