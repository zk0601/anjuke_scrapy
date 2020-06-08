import requests

url = "https://miniapp.58.com/landlord/getprivacyphone"
headers = {

    #             'P3P': 'policyref="/w3c/p3p.xml", CP="CUR ADM OUR NOR STA NID"',

}

payload = {
            # "from":"58_ershoufang",
            # "app":"a-wb",
            # "from":"58_ershoufang",
            # "platform":"windows",
            # "b":"microsoft",
            # "s":"win10",
            # "wcv":"5.0",
            # "wv":"7.0.9",
            # "sv":"2.10.4",
            # "batteryLevel":"2.10.4",
    "user_id": "72054884585483",
    "info_id": "42358467844118"
}

# print(requests.get(url, params=payload).content)
