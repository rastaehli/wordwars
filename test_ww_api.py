# test_ww_api.py
# assumes you have already started ww_api.py in a local web server via command:
#    dev_appserver.py .

import pprint

from apiclient.discovery import build

def main():
  # Build a service object for interacting with the API.
#  api_root = 'https://guestbook.appspot.com/_ah/api'
  api_root = 'https://localhost:8080/_ah/api'
  api = 'wordwars'
  version = 'v1'
  discovery_url = '%s/discovery/v1/apis/%s/%s/rest' % (api_root, api, version)
  service = build(api, version, discoveryServiceUrl=discovery_url)

  # Fetch all greetings and print them out.
  response = service.users().list().execute()
  pprint.pprint(response)

  # Fetch a single greeting and print it out.
  response = service.users().get(id='1').execute()
  pprint.pprint(response)

if __name__ == '__main__':
  main()