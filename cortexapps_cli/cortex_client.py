import requests
import json
import typer
from rich import print

class CortexClient:
    def __init__(self, api_key, base_url='https://api.getcortexapp.com'):
        self.api_key = api_key
        self.base_url = base_url

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
                error = response.json()
                status = response.status_code
                message = error.get('message', 'Unknown error')
                details = error.get('details', 'No details')
                request_id = error.get('requestId', 'No request ID')
                error_str = f'[red][bold]HTTP Error {status}[/bold][/red]: {message} - {details} [dim](Request ID: {request_id})[/dim]'
                print(error_str)
                raise typer.Exit(code=1)
            except json.JSONDecodeError:
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

    def post(self, endpoint, data={}, headers={}, raw=False):
        return self.request('POST', endpoint, data=data, headers=headers, raw=raw)

    def put(self, endpoint, data={}, headers={}, raw=False):
        return self.request('PUT', endpoint, data=data, headers=headers, raw=raw)

    def delete(self, endpoint, headers={}, raw=False):
        return self.request('DELETE', endpoint, headers=headers, raw=raw)
