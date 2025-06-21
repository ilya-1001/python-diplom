import requests as rq


# response = rq.post("http://0.0.0.0:8000/api/v1/user/register",
#                    json={"first_name": "red", "last_name": "reds", "email": "dngr2013@yandex.ru",
#                          "password": "Fds-987-Hge", "company": "noxc", "position": "0001234"},
#                    )
# print(response)
# print(response.json())
response = rq.post("http://0.0.0.0:8000/api/v1/user/register",
                   json={"first_name": "yellow", "last_name": "yellows", "email": "dngr2011@yandex.ru",
                         "password": "Fdsz-9875-Hge", "company": "noxic", "position": "1001234"},
                   )
print(response)
print(response.json())