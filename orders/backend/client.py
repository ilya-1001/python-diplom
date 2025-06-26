import requests as rq

"""
регистрация покупателя
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/user/register",
#                    json={"first_name": "first_name", "last_name": "last_name",
#                          "username": "username", "email": "example@mail",
#                          "password": "xxx-xxx-xxx", "company": "company", "position": "position"
#                          },
#                    )
# print(response)
# print(response.json())


"""
регистрация продавца
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/user/register",
#                    json={"first_name": "first_name", "last_name": "last_name",
#                          "username": "username", "email": "example@mail",
#                          "password": "xxx-xxx-xxx", "company": "company",
#                          "position": "position", "type": "supplier"
#                          },
#                    )
# print(response)
# print(response.json())


"""
подтверждение электронной почты 
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/user/register/confirm",
#                    json={"email": "example@mail",
#                          "token": "7776af6ed93d1c"},
#                    )
# print(response)
# print(response.json())


"""
авторизация 
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/user/login",
#                       json={"email": "example@mail",
#                             "password": "xxx-xxx-xxx"},
#                    )
# print(response)
# print(response.json())


"""
детальная информация о покупателе/поставщике 
"""
# response = rq.get("http://0.0.0.0:8000/api/v1/user/details",
#                     headers={"Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"},
#                    )
# print(response)
# print(response.json())


"""
редактирование информации о покупателе/поставщике 
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/user/details",
#                     headers={"Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"},
#                     json={"first_name": "first_name",
#                           "last_name": "last_name",
#                           "username": "username",
#                           "email": "example@mail",
#                           "password": "xxx-xxx-xxx",
#                           "company": "company",
#                           "position": "position",
#                           "type": "type"
#                          },
#                    )
# print(response)
# print(response.json())


"""
создать контакт 
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/user/contact",
#                     headers={"Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"},
#                     json={"city": "city",
#                           "street": "street",
#                           "house": "house",
#                           "structure": "structure",
#                           "building": "building",
#                           "apartment": "apartment",
#                           "phone": "3424342536457"
#                           },
# )
# print(response.status_code)
# print(response.json())


"""
редактировать контакт 
"""
# response = rq.put("http://0.0.0.0:8000/api/v1/user/contact",
#                     headers={"Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"},
#                     json={"city": "city",
#                           "street": "street",
#                           "house": "house",
#                           "structure": "structure",
#                           "building": "building",
#                           "apartment": "apartment",
#                           "phone": "3424342536457"
#                           },
# )
# print(response.status_code)
# print(response.json())


"""
информация о  контакте 
"""
# response = rq.get("http://0.0.0.0:8000/api/v1/user/contact",
#                     headers={"Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"}
# )
# print(response.status_code)
# print(response.json())


"""
удалить контакт 
"""
# response = rq.delete("http://0.0.0.0:8000/api/v1/user/contact",
#                     headers={"Content-Type": "application/json",
#                     "Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"},
#                     json={"items": "1"}
# )
# print(response)
# print(response.json())


"""
сбросить пароль
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/user/password_reset",
#                   json={"email": "dngr2013@yandex.ru"}
# )
# print(response.status_code)
# print(response.json())


"""
установить новый пароль 
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/user/password_reset/confirm",
#                   json={"email": "dngr2013@yandex.ru",
#                         "password": "Nds-021-TrA",
#                         "token": "7f373b67f085009df7ea6fc6aba4625c4c53308d77f6e011cd"}
# )
# print(response.status_code)
# print(response.json())


"""
список поставщиков 
"""
# response = rq.get("http://0.0.0.0:8000/api/v1/supplier"
# )
# print(response.status_code)
# print(response.json())


"""
добавить товары в корзину 
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/basket",
#                     headers={"Content-Type": "application/json",
#                         "Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"},
#                     json={"items":
#                                   [
#                                   {"product_info": 1,"quantity": 2}
#                               ]
#                     }
# )
# print(response)
# print(response.json())


"""
редактировать количество товаров в корзине 
"""
# response = rq.put("http://0.0.0.0:8000/api/v1/basket",
#                     headers={"Content-Type": "application/json",
#                         "Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"},
#                     json={"items":
#                                   [
#                                   {"product_info": 1,"quantity": 2}
#                               ]
#                     }
# )
# print(response)
# print(response.json())


"""
удалить товары из корзины
"""
# response = rq.delete("http://0.0.0.0:8000/api/v1/basket",
#                     headers={"Content-Type": "application/json",
#                         "Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"},
#                     json={"items": 15, 7, 4}
# )
# print(response)
# print(response.json())


"""
получить содержимое корзины
"""
# response = rq.get("http://0.0.0.0:8000/api/v1/basket",
#                     headers={"Content-Type": "application/json",
#                         "Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"},
# )
# print(response)
# print(response.json())


"""
получить мои заказы
"""
# response = rq.get("http://0.0.0.0:8000/api/v1/order",
#                     headers={"Content-Type": "application/json",
#                         "Authorization": "Token ff1af57c758402acb9ac1afcafab1f4201a5a3c4"}
# )
# print(response.status_code)
# print(response.json())


"""
разместить заказ
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/order",
#                     headers={"Content-Type": "application/json",
#                         "Authorization": "Token 967d5742833d66852e21fc1c47b8f1a7e6bb635b"},
#                     json={'id': '1',
#                           'contact': 1}
# )
# print(response.status_code)
# print(response.json())


"""
обновить прайс поставщика
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/supplier/update",
#                    headers={"Content-Type": "application/json",
#                             "Authorization": "Token 7cffb2cd6e8e50d6d8de2548824669f133c3c25b"},
#                    json={"url":
#                    "https://raw.githubusercontent.com/ilya-1001/python-diplom/refs/heads/main/orders/supplier1.yaml"}
# )
# print(response.status_code)
# print(response.json())


"""
получить статус поставщика
"""
# response = rq.get("http://0.0.0.0:8000/api/v1/supplier/state",
#                    headers={"Content-Type": "application/json",
#                             "Authorization": "Token 7cffb2cd6e8e50d6d8de2548824669f133c3c25b"},
#                    json={"url":
#                    "https://raw.githubusercontent.com/ilya-1001/python-diplom/refs/heads/main/orders/supplier1.yaml"}
# )
# print(response.status_code)
# print(response.json())


"""
получить сформированные заказы
"""
# response = rq.get("http://0.0.0.0:8000/api/v1/supplier/orders",
#                    headers={"Content-Type": "application/json",
#                             "Authorization": "Token 7cffb2cd6e8e50d6d8de2548824669f133c3c25b"},
#                    json={"url":
#                    "https://raw.githubusercontent.com/ilya-1001/python-diplom/refs/heads/main/orders/supplier1.yaml"}
# )
# print(response.status_code)
# print(response.json())


"""
обновить статус поставщика
"""
# response = rq.post("http://0.0.0.0:8000/api/v1/supplier/state",
#                    headers={"Content-Type": "application/json",
#                             "Authorization": "Token 7cffb2cd6e8e50d6d8de2548824669f133c3c25b"},
#                    json={"state":
#                          "on"}
# )
# print(response.status_code)
# print(response.json())




