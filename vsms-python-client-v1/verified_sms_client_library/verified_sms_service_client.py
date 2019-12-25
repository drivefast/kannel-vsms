# -*- coding: utf-8 -*-
'''This module functions to store hashes and updated keys with Verified SMS'''
import base64
import json
import time
import datetime
import requests
from requests.adapters import HTTPAdapter
import jwt
from urllib3.util import Retry

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_der_private_key
from cryptography.hazmat.primitives.serialization import load_der_public_key
from vsms_python_client_v1.verified_sms_hashing_library.verified_sms_hash_generator import VerifiedSmsHashGenerator

class VerifiedSmsServiceClient(object):
    '''API Client for Verified SMS'''
    _API_ROOT_URL = 'https://verifiedsms.googleapis.com/v1/'

    _generator = VerifiedSmsHashGenerator()

    _auth_token = None
    _api_key = None
    _http_session = None

    def __init__(self, *args, **kwargs):
        '''
        Constructor. Object can be created with either a service account file location
        for authorization or an API key.
        '''
        service_account_location = kwargs.get('service_account_location')
        service_account_as_json = kwargs.get('service_account_as_json')
        self._api_key = kwargs.get('api_key')

        # User file location if available
        if service_account_location:
            service_account_as_json = json.loads(open(service_account_location).read())

        if self._api_key is None:
            self._auth_token = self._get_authorization_token(service_account_as_json)

        self._http_session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 501, 502, 503, 504])
        self._http_session.mount('http://', HTTPAdapter(max_retries=retries))

    def update_key(self, agent_id, public_key_as_bytes):
        '''
        Updates the agent's registered public key.

        Args:
            agent_id (str): The unique agent id.
            public_key_as_bytes (bytes): The new public key to store for this agent.
        '''
        public_key_as_base64_string = base64.urlsafe_b64encode(public_key_as_bytes).decode('utf-8')

        json_body = {'publicKey': public_key_as_base64_string}
        url_part = 'agents/' + agent_id + '/key'

        # Update the agent's public key with Verified SMS
        self._execute_api_all(self._API_ROOT_URL + url_part, json_body, 'patch')

    def get_user_keys(self, phone_numbers):
        '''
        Gets the phone number publics keys associated with each device.

        Args:
            phone_numbers (list): List of phone numbers.

        Returns:
           A :object: Object representing device and public key pairs
        '''
        json_body = {'phoneNumbers': phone_numbers}

        response = self._execute_api_all(self._API_ROOT_URL + 'userKeys:batchGet', json_body)

        user_to_keys = {}

        for value in response['userKeys']:
            user_to_keys[value['phoneNumber']] = value['publicKey']

        return user_to_keys

    def get_agent_public_key(self, agent_id):
        '''
        Gets the most recent public key registered for the given agent id.

        Args:
            agent_id (str): The agent id.

        Returns:
           A :str: The most recently stored agent's public key.
        '''
        response = self._execute_api_all(self._API_ROOT_URL + 'agents/' + agent_id + '/key',
                                         None, 'GET')

        if response['publicKey']:
            return response['publicKey']

        return None

    def create_hashes(self, agent_id, recipient_and_messages, private_key_as_bytes, debug_mode=False):
        '''
        Gets the public hashses associated with the recipients, uses these in combination with
        the agent's private key to calculate message hash values, and then stores those
        hash codes with Verified SMS.

        Args:
            agent_id (str): The registered unique agent id.
            recipient_and_messages (dict): A dictionary of phone number to message mappings.
            private_key_as_bytes (bytes): A byte array of the agent's private key.
            debug_mode (boolean): True if the public key for the agent should be validated
                as part of the API call.

        Returns:
           A :object: The return object from Verified SMS.
        '''
        user_to_keys = self.get_user_keys(list(recipient_and_messages.keys()))

        private_ec_key = load_der_private_key(private_key_as_bytes,
                                              password=None, backend=default_backend())

        hash_codes = self._calculate_hashes(recipient_and_messages, private_ec_key, user_to_keys)

        # Check debug flag, if true, calculate the public key based on the private key
        # and pass it through to the API for validation
        # Note: This should not be used in production, should only be used for testing
        if debug_mode:
            public_key = private_ec_key.public_key().public_bytes(encoding=serialization.Encoding.DER,
                                                                  format=serialization.PublicFormat.SubjectPublicKeyInfo)

            public_key_as_base64_string = base64.urlsafe_b64encode(public_key).decode('utf-8')

            json_body = {'hashes': {'values': hash_codes}, 'publicKey': public_key_as_base64_string}
        else:
            json_body = {'hashes': {'values': hash_codes}}

        url_part = 'agents/' + agent_id + ':storeHashes'

        # Store the hashes with Verified SMS
        response = self._execute_api_all(self._API_ROOT_URL + url_part, json_body)

        return response

    def _calculate_hashes(self, recipient_and_messages, private_ec_key, user_to_keys):
        '''
        Iterates over the phone number to message pairs and calculates hash codes
        for each combination.

        Args:
            recipient_and_messages (dict): Phone number to message mapping.
            private_ec_key (EllipticCurvePrivateKey): The agent's private key.
            user_to_keys (dict): Mapping of phone number to public key pairs.

        Returns:
           A :list: List of hash codes for all messages.
        '''
        all_hash_codes = []

        for phone_number, message in recipient_and_messages.items():
            public_device_key = user_to_keys[phone_number]
            public_device_key_as_binary = base64.b64decode(public_device_key)
            public_ec_key = load_der_public_key(public_device_key_as_binary,
                                                backend=default_backend())

            # Compute hash code for this private/public key combination and message
            hash_codes = self._generator.create_hashes(private_ec_key, public_ec_key, message)
            all_hash_codes.extend(hash_codes)

        return all_hash_codes

    def _execute_api_all(self, api_endpoint_url, json_body, method='POST'):
        '''
        Executes the API call with Verified SMS.

        Args:
            api_endpoint_url (str): The API endpoint to call.
            json_body (str): The JSON body to POST to the endpoint.

        Returns:
           A :object: The JSON returned by the API call.
        '''
        json_as_string = json.dumps(json_body)

        if self._api_key is None:
            headers = {'authorization': 'Bearer ' + self._auth_token,
                       'content-type': 'application/json'}
        else:
            headers = {'content-type': 'application/json'}
            api_endpoint_url += '?key=' + self._api_key

        if method == 'POST':
            content = self._http_session.post(url=api_endpoint_url,
                                              data=json_as_string, headers=headers)
        elif method == 'GET':
            content = self._http_session.get(url=api_endpoint_url,
                                             headers=headers)
        else:
            content = self._http_session.patch(url=api_endpoint_url,
                                               data=json_as_string, headers=headers)

        if content.status_code == 200:
            return json.loads(content.text)

        raise Exception(content.text)

    def _get_authorization_token(self, service_account_as_json):
        '''
        Initializes authentication for API calls with a service account.

        Args:
            service_account_as_json (str): The json object service account key info.

        Returns:
           A :str: The auth token to be used for API calls.
        '''
        key = service_account_as_json['private_key']
        ts = time.time()
        pattern = '%d.%m.%Y %H.%M.%S'
        date_time = datetime.datetime.fromtimestamp(ts).strftime(pattern)
        epoch = int(time.mktime(time.strptime(date_time, pattern)))

        claim = {
            'iss': service_account_as_json['client_email'],
            'scope': 'https://www.googleapis.com/auth/verifiedsms',
            'aud': 'https://www.googleapis.com/oauth2/v4/token',
            'exp': epoch,
            'iat': epoch
        }

        token = jwt.encode(claim, key, algorithm='RS256')
        r = requests.post('https://www.googleapis.com/oauth2/v4/token',
                          data={
                              'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                              'assertion': token
                          })

        response_data = json.loads(r.text)
        auth_token = response_data['access_token']

        return auth_token
