import requests
import json

url = "https://prod-126.westeurope.logic.azure.com:443/workflows/facba28a90494be696403f3ac5d30e76/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=ksuvRvHmXHHiSx4PmfqfwK0u-O1GnZLcw2SsDw_nYi0"

payload = json.dumps({
  "date_from": "2024-09-19T00:00:00.511Z",
  "date_to": "2024-09-22T18:25:43.511Z",
  "key": "2E756301B3B521EAF8ADD3D17209ECA9FEB6A707F99B9B5A3B15931941D2AD88"
})
headers = {
  'Content-Type': 'application/json',
  'Cookie': 'ARRAffinity=9edc003cc660166aa7bf544e48b3f9fd53451e8f86e937567abd1101172052be; ARRAffinitySameSite=9edc003cc660166aa7bf544e48b3f9fd53451e8f86e937567abd1101172052be'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
