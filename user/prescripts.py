from user.models import AppConfiguration

def insertAppConfiguration():
    print('**********Writing the default configuration*******************')
    conf = {
        'issuer': 'https://tecnics-dev.oktapreview.com',
        'clientId': '0oaz68of4x7liz5x60h7',
        'scopes': ["openid", "email", "profile"]
    }
    AppConfiguration.objects.get_or_create(title="widget", configuration=conf)
