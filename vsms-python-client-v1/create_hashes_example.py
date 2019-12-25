# -*- coding: utf-8 -*-
# Copyright 2018 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''This example reads the Verified SMS agent's private key, creates hash codes for specified
recipients and SMS messages, and synchronously sends the hash codes to Verified SMS. Before
running the example, set up environment variables with the following commands:

export VERIFIED_SMS_AGENT_ID="google-testing-agent"
VERIFIED_SMS_SERVICE_ACCOUNT_PATH="/path/to/service-account.json"
export VERIFIED_SMS_PRIVATE_KEY_PATH="/path/to/private-key-pkcs8.der"

This example requires a private key in PKCS#8 format from private-key-pkcs8.der.

Generate keys in PEM, PKCS#8, and x.509 formats with the following commands:

private-key.pem: private key in PEM format
private-key-pkcs8.der: private key in PKCS#8 format, readable by Java
public-key.der: public key in X.509 format, readable by Java

openssl ecparam -name secp384r1 -genkey -outform PEM -noout -out private-key.pem
openssl pkcs8 -topk8 -nocrypt -in private-key.pem -outform DER -out private-key-pkcs8.der
openssl ec -in private-key.pem -pubout -outform DER -out public-key.der
'''
import os
import json
from verified_sms_client_library.verified_sms_service_client import VerifiedSmsServiceClient

def main():
    # Read environment variables
    if ('VERIFIED_SMS_AGENT_ID' in os.environ and
            'VERIFIED_SMS_PRIVATE_KEY_PATH' in os.environ and
            'VERIFIED_SMS_SERVICE_ACCOUNT_PATH' in os.environ):
        agent_id = os.environ['VERIFIED_SMS_AGENT_ID']
        private_key_path = os.environ['VERIFIED_SMS_PRIVATE_KEY_PATH']
        service_account_location = os.environ['VERIFIED_SMS_SERVICE_ACCOUNT_PATH']
    else:
        print('The environment variables required for this sample are not set. Please check the '
              + 'README file and setup the required environment variables in order to run this '
              + 'sample.')
        exit()

    # Read the private key file
    with open(private_key_path, mode='rb') as file:
        print('Reading the agent\'s private key ...')
        private_key_as_bytes = file.read()

        service_account_as_json = json.loads(open(service_account_location).read())

        print('Creating the Verified SMS Api Client ...')

        vsms_service_client = VerifiedSmsServiceClient(
            service_account_as_json=service_account_as_json)

        sms = 'Hello, simple post world!'
        recipient_and_messages = {'+16509999996': sms + '1',
                                  '+16509999997': sms + '2',
                                  '+16509999998': sms + '3',
                                  '+16509999999': sms + '4'}

        print('Storing hash codes for SMS messages')

        # NOTE: debug_mode=True in this call should only be
        # used for testing, not in production
        response = vsms_service_client.create_hashes(agent_id, recipient_and_messages,
                                                     private_key_as_bytes, debug_mode=True)

        if response is not None:
            print('Storing hash codes was successful.')
            print('Response body from server:')
            print(response)

        # TODO: Send the actual SMS message

if __name__ == '__main__':
    main()
# [END app]
