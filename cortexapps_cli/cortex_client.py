import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import typer
from rich import print
from rich import print_json
from rich.markdown import Markdown
from rich.console import Console
import logging
import urllib.parse
import time
import threading
import os

from cortexapps_cli.utils import guess_data_key


class TokenBucket:
    """
    Token bucket rate limiter for client-side rate limiting.

    Allows bursts up to bucket capacity while enforcing long-term rate limit.
    Thread-safe for concurrent use.
    """
    def __init__(self, rate, capacity=None):
        """
        Args:
            rate: Tokens per second (e.g., 1000 req/min = 16.67 req/sec)
            capacity: Maximum tokens in bucket (default: rate, allows 1 second burst)
        """
        self.rate = rate
        self.capacity = capacity or rate
        self.tokens = self.capacity
        self.last_update = time.time()
        self.lock = threading.Lock()

    def acquire(self, tokens=1):
        """
        Acquire tokens, blocking until available.

        Args:
            tokens: Number of tokens to acquire (default: 1)
        """
        with self.lock:
            while True:
                now = time.time()
                elapsed = now - self.last_update

                # Refill tokens based on elapsed time
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return

                # Calculate wait time for next token
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate

                # Release lock and sleep
                self.lock.release()
                time.sleep(min(wait_time, 0.1))  # Sleep in small increments
                self.lock.acquire()


class CortexClient:
    def __init__(self, api_key, tenant, numeric_level, base_url='https://api.getcortexapp.com', rate_limit=None):
        self.api_key = api_key
        self.tenant = tenant
        self.base_url = base_url

        logging.basicConfig(level=numeric_level)
        self.logger = logging.getLogger(__name__)

        # Enable urllib3 retry logging to see when retries occur
        urllib3_logger = logging.getLogger('urllib3.util.retry')
        urllib3_logger.setLevel(logging.DEBUG)

        # Read rate limit from environment variable or use default
        if rate_limit is None:
            rate_limit = int(os.environ.get('CORTEX_RATE_LIMIT', '1000'))

        # Client-side rate limiter (default: 1000 req/min = 16.67 req/sec)
        # Allows bursting up to 50 requests, then enforces rate limit
        self.rate_limiter = TokenBucket(rate=rate_limit/60.0, capacity=50)

        # Create a session with connection pooling for better performance
        self.session = requests.Session()

        # Configure connection pool to support concurrent requests
        # pool_connections: number of connection pools to cache
        # pool_maxsize: maximum number of connections to save in the pool
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=50,
            max_retries=Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[429],  # Only retry on rate limit errors
                allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
                respect_retry_after_header=True
            )
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

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

        # Use session for connection pooling and reuse
        # Acquire rate limit token before making request (blocks if needed)
        self.rate_limiter.acquire()

        start_time = time.time()
        response = self.session.request(method, url, params=params, headers=req_headers, data=req_data)
        duration = time.time() - start_time

        # Log slow requests or non-200 responses (likely retries happened)
        if duration > 2.0 or response.status_code != 200:
            self.logger.info(f"{method} {endpoint} -> {response.status_code} ({duration:.1f}s)")

        # Log if retries likely occurred (duration suggests backoff delays)
        if duration > 5.0:
            self.logger.warning(f"⚠️  Slow request ({duration:.1f}s) - likely retries occurred")

        self.logger.debug(f"Request Headers: {response.request.headers}")
        self.logger.debug(f"Response Status Code: {response.status_code}")
        self.logger.debug(f"Response Headers: {response.headers}")
        self.logger.debug(f"Response Content: {response.text}")

        # Check if response is OK. Note: urllib3 Retry with status_forcelist should have already
        # retried any 429/500/502/503/504 errors. If we're here with one of those status codes,
        # it means retries were exhausted.

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
