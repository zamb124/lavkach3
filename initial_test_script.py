import requests

user_id = None

user = {
  "email": "loh@loh2.ru",
  "password1": "1402",
  "password2": "1402",
  "nickname": "loh2"
}
responce = requests.post('http://127.0.0.1:8080/api/users', json=user)
user_id = responce.json().get('')
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

responce1 = requests.post('http://127.0.0.1:8080/api/store/create', json=store1)
responce2 = requests.post('http://127.0.0.1:8080/api/store/create', json=store2)

store1_id = responce1.json().get('id')
store2_id = responce2.json().get('id')

#839a34aa-346c-48c8-b6d9-a8e3a98d60fd
contractor1 = {
  "title": "Contractor 1",
  "external_id": "1",
  "company_id": "2998d79d-e942-4919-bff0-2c6dfa9e0a99"
}
#06425cb2-6fec-478e-91f7-eadb6dfa4fb7
contractor2 = {
  "title": "Contractor 2",
  "external_id": "2",
  "company_id": "2998d79d-e942-4919-bff0-2c6dfa9e0a99"
}
responce1 = requests.post('http://127.0.0.1:8080/api/contractor/create', json=contractor1)
responce2 = requests.post('http://127.0.0.1:8080/api/contractor/create', json=contractor2)

contractor1_id = responce1.json().get('id')
contractor2_id = responce2.json().get('id')

#83dca62d-eba3-4c60-a073-94df92b04cd6
supplier1 = {
  "title": "Supplier 1 ",
  "external_id": "1",
  "contractor_id": contractor1_id
}

#3a7335cf-0be8-4360-bc9b-625973db0a1
supplier2 = {
  "title": "Supplier 2 ",
  "external_id": "2",
  "contractor_id": contractor2_id
}

responce1 = requests.post('http://127.0.0.1:8080/api/supplier/create', json=supplier1)
responce2 = requests.post('http://127.0.0.1:8080/api/supplier/create', json=supplier2)

supplier1_id = responce1.json().get('id')
supplier2_id = responce2.json().get('id')

#7e7aa833-9c7b-493b-9b79-1bf11431b767
manufact1 = {
  "title": "Manufacturer 1",
  "company_id": company_id
}
#6498c629-f4d0-49de-816c-66ba3ee977b1
manufact2 = {
  "title": "Manufacturer 2",
  "company_id": company_id
}
#cd479362-c5a2-4152-949c-30684125adb2
manufact3 = {
  "title": "Manufacturer 3",
  "company_id": company_id
}
#b2bb550c-b450-45a2-a122-e22b2a141de5
manufact4 = {
  "title": "Manufacturer 4",
  "company_id": company_id
}

responce1 = requests.post('http://127.0.0.1:8080/api/manufacturer/create', json=manufact1)
responce2 = requests.post('http://127.0.0.1:8080/api/manufacturer/create', json=manufact2)
responce3 = requests.post('http://127.0.0.1:8080/api/manufacturer/create', json=manufact3)
responce4 = requests.post('http://127.0.0.1:8080/api/manufacturer/create', json=manufact4)

manufact1 = responce1.json().get('id')
manufact2 = responce2.json().get('id')
manufact3 = responce1.json().get('id')
manufact4 = responce2.json().get('id')
manuls = (manufact1, manufact2, manufact3, manufact4)
for i, m in enumerate(manuls):
  body = {
  "title": f"Model {i}",
  "manufacturer_id": m
}
  responce = requests.post('http://127.0.0.1:8080/api/model/create', json=body)
  model = responce.json().get('id')

  #95484185-385d-4f63-8565-bb779bef1177
  asset_type = {
  "title": f"Asset Type {i}",
  "company_id": company_id,
  "type": "storable",
  "source": "internal",
  "serial_required": True
}
  responce = requests.post('http://127.0.0.1:8080/api/assets_type/create', json=asset_type)
  asset_type_id = responce.json().get('id')

  asset = {
  "title": f"Asset {i}",
  "company_id": company_id,
  "asset_type_id": asset_type_id,
  "manufacturer_id": manufact1,
  "store_id": store1_id,
  "model_id": model,
  "status": "draft",
  "serial": f"2312312312{i}",
  "at": f"Htoto {i}",
  "user_id": user_id
}