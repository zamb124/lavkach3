import requests
import uuid
user_id = "cf144389-410c-4c06-b2de-18dc37432858"
#url = 'http://158.160.53.137:8080/'
url = 'http://0.0.0.0:8080'
user = {
  "email": "loh@loh2.ru",
  "password1": "1402",
  "password2": "1402",
  "nickname": "loh2"
}
responce = requests.post('http://158.160.53.137:8080/api/users', json=user)
print(responce.status_code)

company = {
  "title": f"Company 1 {uuid.uuid4().__str__()[:7]}",
  "external_id": f"{uuid.uuid4().__str__()[:7]}",
  "lang": "ruRU",
  "country": "Russia",
  "currency": "RUB"
}
responce = requests.post('http://158.160.53.137:8080/api/company/create', json=company)
print(responce.status_code)
# 2998d79d-e942-4919-bff0-2c6dfa9e0a99
company_id = responce.json().get('id')



#778a19d7-04b9-4cae-a993-3e76dfd60ce9
store1 = {
  "title": f"Store 1 {uuid.uuid4().__str__()[:7]}",
  "external_id": f"{uuid.uuid4().__str__()[:7]}",
  "address": f"Pushka 1 {uuid.uuid4().__str__()[:7]}",
  "source": "internal"
}
#79d679ac-bab3-42c5-8536-ab50e0e24eb1
store2 = {
  "title": f"Store 2{uuid.uuid4().__str__()[:7]}",
  "external_id": f"{uuid.uuid4().__str__()[:7]}",
  "address": f"Pushka 2 {uuid.uuid4().__str__()[:7]}",
  "source": "internal"
}

responce1 = requests.post('http://158.160.53.137:8080/api/store/create', json=store1)
responce2 = requests.post('http://158.160.53.137:8080/api/store/create', json=store2)
print(responce1.status_code)
print(responce2.status_code)
store1_id = responce1.json().get('id')
store2_id = responce2.json().get('id')

#839a34aa-346c-48c8-b6d9-a8e3a98d60fd
contractor1 = {
  "title": f"Contractor 1{uuid.uuid4().__str__()[:7]}",
  "external_id": f"1{uuid.uuid4().__str__()[:7]}",
  "company_id": company_id
}
#06425cb2-6fec-478e-91f7-eadb6dfa4fb7
contractor2 = {
  "title": f"Contractor 2{uuid.uuid4().__str__()[:7]}",
  "external_id": f"{uuid.uuid4().__str__()[:7]}",
  "company_id": company_id
}
responce1 = requests.post('http://158.160.53.137:8080/api/contractor/create', json=contractor1)
responce2 = requests.post('http://158.160.53.137:8080/api/contractor/create', json=contractor2)

contractor1_id = responce1.json().get('id')
contractor2_id = responce2.json().get('id')
print(responce1.status_code)
print(responce2.status_code)

#83dca62d-eba3-4c60-a073-94df92b04cd6
supplier1 = {
  "title": f"Supplier 1 {uuid.uuid4().__str__()[:7]}",
  "external_id": f"{uuid.uuid4().__str__()[:7]}",
  "contractor_id": contractor1_id
}

#3a7335cf-0be8-4360-bc9b-625973db0a1
supplier2 = {
  "title": f"Supplier 2 {uuid.uuid4().__str__()[:7]}",
  "external_id": f"2{uuid.uuid4().__str__()[:7]}",
  "contractor_id": contractor2_id
}

responce1 = requests.post('http://158.160.53.137:8080/api/supplier/create', json=supplier1)
responce2 = requests.post('http://158.160.53.137:8080/api/supplier/create', json=supplier2)
print(responce1.status_code)
print(responce2.status_code)

supplier1_id = responce1.json().get('id')
supplier2_id = responce2.json().get('id')

#7e7aa833-9c7b-493b-9b79-1bf11431b767
manufact1 = {
  "title": f"Manufacturer 1{uuid.uuid4().__str__()[:7]}",
  "company_id": company_id
}
#6498c629-f4d0-49de-816c-66ba3ee977b1
manufact2 = {
  "title": f"Manufacturer 2{uuid.uuid4().__str__()[:7]}",
  "company_id": company_id
}
#cd479362-c5a2-4152-949c-30684125adb2
manufact3 = {
  "title": f"Manufacturer 3{uuid.uuid4().__str__()[:7]}",
  "company_id": company_id
}
#b2bb550c-b450-45a2-a122-e22b2a141de5
manufact4 = {
  "title": f"Manufacturer 4{uuid.uuid4().__str__()[:7]}",
  "company_id": company_id
}

responce1 = requests.post('http://158.160.53.137:8080/api/manufacturer/create', json=manufact1)
responce2 = requests.post('http://158.160.53.137:8080/api/manufacturer/create', json=manufact2)
responce3 = requests.post('http://158.160.53.137:8080/api/manufacturer/create', json=manufact3)
responce4 = requests.post('http://158.160.53.137:8080/api/manufacturer/create', json=manufact4)
print(responce1.status_code)
print(responce2.status_code)
print(responce3.status_code)
print(responce4.status_code)

manufact1 = responce1.json().get('id')
manufact2 = responce2.json().get('id')
manufact3 = responce1.json().get('id')
manufact4 = responce2.json().get('id')
manuls = (manufact1, manufact2, manufact3, manufact4)
for i, m in enumerate(manuls):
  body = {
  "title": f"Model {uuid.uuid4().__str__()[:7]}",
  "manufacturer_id": m
}
  responce = requests.post('http://158.160.53.137:8080/api/model/create', json=body)
  print(responce.status_code)
  model = responce.json().get('id')

  #95484185-385d-4f63-8565-bb779bef1177
  asset_type = {
  "title": f"Asset Type {uuid.uuid4().__str__()[:7]}",
  "company_id": company_id,
  "type": "storable",
  "source": "internal",
  "serial_required": True
}
  responce = requests.post('http://158.160.53.137:8080/api/assets_type/create', json=asset_type)
  asset_type_id = responce.json().get('id')
  print(responce.status_code)

  asset = {
  "title": f"Asset {uuid.uuid4().__str__()[:7]}",
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

  responce = requests.post('http://158.160.53.137:8080/api/asset/create', json=asset)
  asset = responce.json().get('id')
  print('asset', responce.status_code)

  order1 = {
  "description": f"{uuid.uuid4().__str__()[:7]}",
  "supplier_id": supplier1_id,
  "status": "draft",
  "asset_id": asset,
  "store_id": store1_id,
  "user_created_id": user_id,
  "supplier_user_id": user_id
}
  responce1 = requests.post('http://158.160.53.137:8080/api/order/create', json=order1)
  order_resp1 = responce.json().get('id')
  print('order', responce.status_code)

  order_line ={
  "title": f"{uuid.uuid4().__str__()[:7]}",
  "description": f"{uuid.uuid4().__str__()[:7]}",
  "order_id": order_resp1,
  "quantity": 0
}
  responce_line1 = requests.post('http://158.160.53.137:8080/api/order/line/create', json=order_line)
  order_line_resp1 = responce.json().get('id')
  print('order_line2', responce.status_code)

  order_line2 = {
    "title": f"{uuid.uuid4().__str__()[:7]}",
    "description": f"{uuid.uuid4().__str__()[:7]}",
                                               "order_id": order_resp1,
    "quantity": 2
  }
  responce_line2 = requests.post('http://158.160.53.137:8080/api/order/line/create', json=order_line2)
  order_line_resp2 = responce.json().get('id')
  print('order_line2', responce.status_code)



  order2 = {
    "description": f"{uuid.uuid4().__str__()[:7]}",
    "supplier_id": supplier1_id,
    "status": "draft",
    "asset_id": asset,
    "store_id": store1_id,
    "user_created_id": user_id,
    "supplier_user_id": user_id
  }
  responce2 = requests.post('http://158.160.53.137:8080/api/order/create', json=order2)
  order_resp2 = responce.json().get('id')
  print('order', responce.status_code)

  order_line3 = {
    "title": f"{uuid.uuid4().__str__()[:7]}",
    "description": f'{uuid.uuid4().__str__()[:7]}',
                                               "order_id": order_resp2,
    "quantity": 3
  }
  responce_line3 = requests.post('http://158.160.53.137:8080/api/order/line/create', json=order_line3)
  order_line_resp3 = responce.json().get('id')
  print('order_line23', responce.status_code)

  order_line4 = {
    "title": f"{uuid.uuid4().__str__()[:7]}",
    "description": f"{uuid.uuid4().__str__()[:7]}",
                                               "order_id": order_resp2,
    "quantity": 4
  }
  responce_line4 = requests.post('http://158.160.53.137:8080/api/order/line/create', json=order_line4)
  order_line_res44 = responce.json().get('id')
  print('order_line4', responce.status_code)