import requests
import json
import typer
from rich import print

class CortexClient:
    def __init__(self, api_key, base_url='https://api.getcortexapp.com'):
        self.api_key = api_key
        self.base_url = base_url

    def data_key_for_endpoint(self, endpoint):
        end_endpoint = endpoint.split('/')[-1]
        match end_endpoint:
            case 'catalog':
                return 'entities'
            case 'audit-logs':
                return 'logs'
            case 'deploys':
                return 'deployments'
            case _:
                return end_endpoint

    def request(self, method, endpoint, params={}, headers={}, data=None, raw=False):
        req_headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            **headers
        }
        url = '/'.join([self.base_url.rstrip('/'), endpoint.lstrip('/')])
        response = requests.request(method, url, params=params, headers=req_headers, json=data)

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
        if raw:
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

    def get(self, endpoint, params={}, headers={}, raw=False):
        return self.request('GET', endpoint, params=params, headers=headers, raw=raw)

    def post(self, endpoint, data={}, params={}, headers={}, raw=False):
        return self.request('POST', endpoint, data=data, params=params, headers=headers, raw=raw)

    def put(self, endpoint, data={}, params={}, headers={}, raw=False):
        return self.request('PUT', endpoint, data=data, params=params, headers=headers, raw=raw)

    def delete(self, endpoint, params={}, headers={}, raw=False):
        return self.request('DELETE', endpoint, params=params, headers=headers, raw=raw)
    
    def fetch(self, endpoint, params={}, headers={}):
        # do paginated fetch, page number is indexed at 0
        # param page is page number, param pageSize is page size, default 250
        page = 0
        page_size = 250
        data_key = self.data_key_for_endpoint(endpoint)
        data = []
        while True:
            response = self.get(endpoint, params={**params, 'page': page, 'pageSize': page_size}, headers=headers)
            if data_key not in response or not response[data_key]:
                break
            data.extend(response[data_key])
            if response['totalPages'] == page + 1:
                break
            page += 1
        return {
            "total": len(data),
            "page": 0,
            "totalPages": 1 if data else 0,
            data_key: data,
        }

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
