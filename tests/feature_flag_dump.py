import os
import requests
import sys

file = sys.argv[1]

h = {
     "Authorization": "Bearer " + os.getenv('CORTEX_API_KEY')
}

url = os.getenv('CORTEX_BASE_URL') + "/api/internal/v1/cortex/preferences"
print("ff url = " + url)
print("key = " + os.getenv('CORTEX_API_KEY'))

try:
    print("here in the try")
    r = requests.get(url, headers=h)
    r.raise_for_status()
except requests.exceptions.RequestException as e:
    print("here in the except")
    print(e.response.text)
    sys.exit(1)

print("outside the try")
print("feature flags = " + r.text)
f = open(file, "w")
f.write(r.text)
f.close()
