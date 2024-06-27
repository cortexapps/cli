import os
import requests
import sys

file = sys.argv[1]

h = {
     "Authorization": "Bearer " + os.getenv('CORTEX_API_KEY')
}

url = os.getenv('CORTEX_BASE_URL') + "/api/internal/v1/cortex/preferences"
print("ff url = " + url)

try:
    r = requests.get(url, headers=h)
    r.raise_for_status()
except requests.exceptions.RequestException as e:
    print(e.response.text)
    sys.exit(1)

print("feature flags = " + r.text)
f = open(file, "w")
f.write(r.text)
f.close()
