import requests

user = {
  "email": "loh@loh2.ru",
  "password1": "1402",
  "password2": "1402",
  "nickname": "loh2"
}
responce = requests.post('http://127.0.0.1:8080/api/users', json=user)
print(responce.status_code)

company = {
  "title": "Company 1",
  "external_id": "1",
  "lang": "ruRU",
  "country": "Russia",
  "currency": "RUB"
}
responce = requests.post('http://127.0.0.1:8080/api/company/create', json=company)
# 2998d79d-e942-4919-bff0-2c6dfa9e0a99
company_id = responce.json().get('id')
#778a19d7-04b9-4cae-a993-3e76dfd60ce9
store1 = {
  "title": "Store 1",
  "external_id": "1",
  "address": "Pushka 1",
  "source": "internal"
}
#79d679ac-bab3-42c5-8536-ab50e0e24eb1
store2 = {
  "title": "Store 2",
  "external_id": "2",
  "address": "Pushka 2",
  "source": "internal"
}

responce1 = requests.post('http://127.0.0.1:8080/api/company/create', json=company)
responce2 = requests.post('http://127.0.0.1:8080/api/company/create', json=company)

store1_id = responce1.json().get('id')
store2_id = responce1.json().get('id')


