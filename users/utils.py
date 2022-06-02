from datetime import datetime, timedelta
from calendar import timegm
import json
from twilio.rest import Client
import pyotp
from core.settings import TWILIO, GRAPHQL_JWT
from graphql_jwt.settings import jwt_settings
from core.utils import AuthMethod
# from core.utils import redis_instance
import redis
import jwt

redis_instance = redis.StrictRedis()

TEMP_REG_EXP = 3600
OTP_EXP_TIME_MIN = 2

class OTPExpireAt(object):

    def __init__(self, time_minutes):

        self.time_minutes = time_minutes
        super().__init__()

    def otp_expire_at(self):
        current_time = datetime.utcnow()
        # Add 2 minutes to datetime object containing current time
        # otp_expire_at = current_time + timedelta(minutes=self.time_minutes)
        otp_expire_at = timegm((current_time + timedelta(minutes=self.time_minutes)).utctimetuple())
        return otp_expire_at

def send_twilio_otp(mobile_number):
    account_sid = TWILIO['ACCOUNT_SID']
    auth_token = TWILIO['AUTH_TOKEN']
    # client = Client(account_sid, auth_token)
    otp_fact = pyotp.TOTP('base32secret3232')
    otp = otp_fact.now()
    # body = f'Welcome to Big Bag, to complete your registeration, enter the OTP: {otp}'

    # message = client.messages.create(  
    #     messaging_service_sid=TWILIO['MESSAGING_SERVICE_SID'],
    #     to=mobile_number,
    #     body=body
    # ) 
    
    # print(message.sid)

    return otp

def validate_otp_and_token(token, otp):
    try:
        print(f'received token {token}')
        user = jwt.decode(
            token,
            GRAPHQL_JWT['JWT_TEMP_SECRET'],
            jwt_settings.JWT_VERIFY,
            options={
                'verify_exp': True,
            },            
            algorithms=[jwt_settings.JWT_ALGORITHM],
        )
        print(f'extracted user {user}')

        data = json.loads(redis_instance.get(user['username']))
        
        if data is None:
            raise ValueError('Error: token is no longer valid')

        print('fetched cache', data)
        otp_exp_ms = data['otp_exp']
        orig_otp = data['otp']
        otp_exp_date = datetime.utcfromtimestamp(otp_exp_ms)
        print(otp_exp_date)

        if datetime.utcnow() < otp_exp_date:                
            if orig_otp == otp:
                print('OTP match && within OTP time')
        else:
            print('OTP timeout')
        
        # return payload
        return user
    except Exception as e:
        print('an error occured', e)
        raise ValueError(f'{e}')


def create_otp_token(user, context=None, **extra):
    # payload = jwt_settings.JWT_PAYLOAD_HANDLER(user, context)
    # payload.update(extra)
    payload = {
        'username': user.username,
        'uid': str(user.id),
        'auth_method': str(user.auth_method.MOBILE),
        'exp': timegm((datetime.utcnow() + jwt_settings.JWT_EXPIRATION_DELTA).utctimetuple()),
        'iat': timegm(datetime.utcnow().utctimetuple())
    }
    
    token = jwt.encode(
        payload,
        GRAPHQL_JWT['JWT_TEMP_SECRET'],
        jwt_settings.JWT_ALGORITHM,        
    ).decode('utf-8')

    print('created token', token)

    otp_exp_obj = OTPExpireAt(OTP_EXP_TIME_MIN)
    otp_exp_at_ = otp_exp_obj.otp_expire_at()


    otp = None

    if user.auth_method == AuthMethod.MOBILE:
        otp = send_twilio_otp(user.username)
    
    data = json.dumps({'token': token, 'password': user.password,
    'otp_exp': otp_exp_at_, 'otp': otp })

    redis_instance.set(user.username, data, TEMP_REG_EXP)

    return {'token': token, 'otp': otp}
