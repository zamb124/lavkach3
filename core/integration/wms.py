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
