import requests
import json
import typer
from rich import print
from rich import print_json
from rich.markdown import Markdown
from rich.console import Console
import logging
import urllib.parse

from cortexapps_cli.utils import guess_data_key


class CortexClient:
    def __init__(self, api_key, tenant, numeric_level, base_url='https://api.getcortexapp.com'):
        self.api_key = api_key
        self.tenant = tenant
        self.base_url = base_url

        logging.basicConfig(level=numeric_level)
        self.logger = logging.getLogger(__name__)

    def request(self, method, endpoint, params={}, headers={}, data=None, raw_body=False, raw_response=False, content_type='application/json'):
        req_headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': content_type,
            **headers
        }
        url = '/'.join([self.base_url.rstrip('/'), endpoint.lstrip('/')])

        req_data = data
        if not raw_body:
            if content_type == 'application/json' and isinstance(data, dict):
                req_data = json.dumps(data)

        response = requests.request(method, url, params=params, headers=req_headers, data=req_data)

        self.logger.debug(f"Request Headers: {response.request.headers}")
        self.logger.debug(f"Response Status Code: {response.status_code}")
        self.logger.debug(f"Response Headers: {response.headers}")
        self.logger.debug(f"Response Content: {response.text}")

        if not response.ok:
            try:
                # try to parse the error message
                error = response.json()
                status = response.status_code
                message = error.get('message', 'Unknown error')
                details = error.get('details', 'No details')
                request_id = error.get('requestId', 'No request ID')
                error_str = f'[red][bold]HTTP Error {status}[/bold][/red]: {message} - {details} [dim](Request ID: {request_id})[/dim]'
                print(error_str)
                raise typer.Exit(code=1)
            except json.JSONDecodeError:
                # if we can't parse the error message, just raise the HTTP error
                response.raise_for_status()

        if raw_response:
            return response

        try:
            return response.json()
        except json.JSONDecodeError:
            if isinstance(response.text, str):
                return response.text
            elif isinstance(response.content, bytes):
                return response.content
            else:
                return None

    def get(self, endpoint, params={}, headers={}, raw_response=False, content_type='application/yaml'):
        return self.request('GET', endpoint, params=params, headers=headers, raw_response=raw_response, content_type=content_type)

    def post(self, endpoint, data={}, params={}, headers={}, raw_body=False, raw_response=False, content_type='application/json'):
        return self.request('POST', endpoint, data=data, params=params, headers=headers, raw_body=raw_body, raw_response=raw_response, content_type=content_type)

    def put(self, endpoint, data={}, params={}, headers={}, raw_body=False, raw_response=False, content_type='application/json'):
        return self.request('PUT', endpoint, data=data, params=params, headers=headers, raw_body=raw_body, raw_response=raw_response, content_type=content_type)

    def patch(self, endpoint, data={}, params={}, headers={}, raw_body=False, raw_response=False, content_type='application/json'):
        return self.request('PATCH', endpoint, data=data, params=params, headers=headers, raw_body=raw_body, raw_response=raw_response, content_type=content_type)

    def delete(self, endpoint, data={}, params={}, headers={}, raw_response=False):
        return self.request('DELETE', endpoint, data=data, params=params, headers=headers, raw_response=raw_response)

    def fetch(self, endpoint, params={}, headers={}):
        # do paginated fetch, page number is indexed at 0
        # param page is page number, param pageSize is page size, default 250
        page = 0
        page_size = 250
        data_key = None
        data = []
        while True:
            response = self.get(endpoint, params={**params, 'page': page, 'pageSize': page_size}, headers=headers)
            if not (isinstance(response, dict) or isinstance(response, list)):
                # something is terribly wrong; this is definitely not a paginated response
                break

            if data_key is None:
                # first page, guess the data key
                data_key = guess_data_key(response)

            # Some endpoints just return an array as the root element. In those cases, data_key is ''
            if data_key == '':
                # if the data key is empty, the response is a list; an empty list means no more data
                if len(response) == 0:
                    break
                data.extend(response)
            else:
                if data_key not in response or not response[data_key]:
                    break
                data.extend(response[data_key])
                if response['totalPages'] == page + 1:
                    break
            page += 1

        if data_key == '':
            return data

        return {
            "total": len(data),
            "page": 0,
            "totalPages": 1 if data else 0,
            data_key: data,
        }

    def fetch_or_get(self, endpoint, page, prt, params={}):
        if page is None:
            # if page is not specified, we want to fetch all pages
            r = self.fetch(endpoint, params=params)
        else:
            # if page is specified, we want to fetch only that page
            r = self.get(endpoint, params=params)

        if prt:
            print_json(data=r)
        else:
            return(r)


    def get_entity(self, entity_tag: str, entity_type: str = ''):
        match entity_type.lower():
            case 'team' | 'teams':
                path_for_type = 'teams'
            case _:
                path_for_type = 'catalog'

        return self.get(f'api/v1/{path_for_type}/{entity_tag}')

    def delete_entity(self, entity_tag: str, entity_type: str = ''):
        match entity_type.lower():
            case 'team' | 'teams':
                path_for_type = 'teams'
            case _:
                path_for_type = 'catalog'

        return self.delete(f'api/v1/{path_for_type}/{entity_tag}')

    def archive_entity(self, entity_tag: str, entity_type: str = ''):
        match entity_type.lower():
            case 'team' | 'teams':
                path_for_type = 'teams'
            case _:
                path_for_type = 'catalog'

        return self.put(f'api/v1/{path_for_type}/{entity_tag}/archive')

    def unarchive_entity(self, entity_tag: str, entity_type: str = ''):
        match entity_type.lower():
            case 'team' | 'teams':
                path_for_type = 'teams'
            case _:
                path_for_type = 'catalog'

        return self.put(f'api/v1/{path_for_type}/{entity_tag}/unarchive')

    def read_file(self, file):
        return file.read()
