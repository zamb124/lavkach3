import requests

WMS_URL = {
    'testing': 'https://lavka-api-proxy.lavka.yandex.net',
    'production': 'https://api.lavka.yandex.net',
}


class ClientWMS():

    @classmethod
    async def req(cls, cursor, path, token):
        response = requests.post(
            WMS_URL['production'] + path,
            json={'cursor': cursor},
            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token},
            timeout=5,
        )
        if response is None:
            return None
        if response.status_code != 200:
            return None
        response = response.json()
        return response

    @classmethod
    async def assign_device(cls, barcode, path):
        response = requests.post(
            WMS_URL['production'] + path,
            json={'barcode': barcode, 'device': '14fc3a62-10f6-11ea-8fac-8fd23d4204eb'},
            headers={'Content-Type': 'application/json'},
            timeout=3,
        )
        if response.status_code != 200:
            return response.status_code
        response = response.json()
        return response
