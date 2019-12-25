VERIFIED SMS: FIRST AGENT DEMONSTRATION

This sample Verified SMS sample demonstrates how to use the Verified SMS Python SDK to hash SMS
messages prior to sending the hashed values to the Verified SMS API endpoint.


PREREQUISITES

You must have the following software installed on your development machine:

* [Python](https://www.python.org/downloads/) - version 3.0 or above
* [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)

You must also have already registered an agent for Verified SMS. See instructions here:
https://developers.google.com/business-communications/verified-sms/guides/build/agents/

You also need to gather information related to your Verified SMS agent:

*   Agent ID
*   Path to the agent's public key on your development machine
*   Path to the agent's private key on your development machine


OVERVIEW

The main class of the Verified SMS client library is VerifiedSmsServiceClient. It contains methods
to update the public key of a Verified SMS agent and store message hashes with Verified SMS. 

This sample consists of the following runnable Python files:

  1. update_agents_key_example.py: Updates an agent's public key through the REST API.
  3. create_hashes_example.py: Stores message hashes synchronously through the REST API.

The Verified SMS client library requires either an API key or service account. Please read each
example's to understand what it requires and set up environment variables accordingly.


SETUP THE SAMPLE:

1. Open [Google Cloud Console](https://console.cloud.google.com/) with your Verified SMS Platform
Google account and find the project you created for your Verified SMS agent.

2. Navigate to the [Verified SMS](https://console.cloud.google.com/apis/library/verifiedsms.googleapis.com)
API library entry and enable the Verified SMS API.

3. Choose how you want to authenticate API calls.

*   Service account

    1. Navigate to [Credentials](https://console.cloud.google.com/apis/credentials).

    2. Click **Create service account**.

    3. For **Service account name**, enter your agent's name, then click **Create**.

    4. For **Select a role**, choose **Project** > **Editor**, the click **Continue**.

    5. Under **Create key**, choose **JSON**, then click **Create**.

       Your browser downloads the service account key. Store it in a secure location.

    6. Click **Done**.

    7. Use the path to the downloaded file to set up the VERIFIED_SMS_SERVICE_ACCOUNT_PATH variable below.

*   API key:

    1. Navigate to [Credentials](https://console.cloud.google.com/apis/credentials)

    2. Click **Create credentials** > **API key**, then click **Restrict key**.

    3. Under **API restrictions**, choose **Restrict key**, and select **Verified SMS API**.

    4. Click **Save**.

    5. Save the API key to your development machine, and use it to set up the VERIFIED_SMS_API_KEY variable below.

Service account:

1. Navigate to https://console.cloud.google.com/apis/credentials and click "Manage service accounts"

2. Create a new service account. Create private key of type JSON, download it as a file and store
the file securely because this key can't be recovered if lost. Use the path to the downloaded file
to set up VERIFIED_SMS_SERVICE_ACCOUNT_PATH variable below.


PREPARE THE SAMPLE:

1. In a terminal, navigate to this sample's root directory.

2. Run the following commands:

virtualenv env
source env/bin/activate
pip install -r requirements.txt


RUN THE SAMPLE:

1. In a terminal, navigate to this sample's root directory.

2. Run the following commands to set up environment variables:

    export VERIFIED_SMS_AGENT_ID="your_verified_sms_agent_id"
    export VERIFIED_SMS_PUBLIC_KEY_PATH="/path/to/public-key.der"
    export VERIFIED_SMS_PRIVATE_KEY_PATH="/path/to/private-key-pkcs8.der"

    If you're using a service account, run the following command:

        export VERIFIED_SMS_SERVICE_ACCOUNT_PATH="/path/to/verified-sms-service-account.json"

    If you're using an API key, run the following command:

        export VERIFIED_SMS_API_KEY="API_KEY_CHARACTERS

3. Run the methods:

  * Update agent public key:

     python update_agents_key_example.py

  * Store hashes:

    python create_hashes_example.py
 
