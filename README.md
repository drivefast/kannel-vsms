## Verified SMS - Kannel adapter


### What is this?

Business SMS providers submit text messages to aggregators either by calling proprietary APIs, or via SMPP - a specialized SMS protocol. Kannel ([www.kannel.org](www.kannel.org)) is a well known SMPP gateway. This Verified SMS kannel adapter operates as a proxy between your app and a kannel SMPP gateway, providing the capability to send out the Verified SMS message hashes, prior to sending the text message itself. Full documentation about the Verified SMS service can be found on the [Google developers website](https://developers.google.com/business-communications/verified-sms).

Under normal circumstances, the vSMS kannel adapter would be transparent to the application that sends your messages to the kannel gateway. The only change in your application is, typically, the URL of the gateway that the message is sent to. Exceptions may have to do with special content encodings you use with your transmissions.


### How it works

Instead of sending http requests to your kannel gateway, you would send them to the vSMS adapter. The adapter would look up the origination number for the message (either shortcode or regular phone number), and will try to find a vSMS agent that registered it. If found, it will first upload the hash of the message, using the Google vSMS SDK, then forward your message to kannel. 

The adapter takes care of splitting long messages and selecting the appropriate encoding. If your application already does this, you may want to simplify it to just send the entire message content as a single request. The kannel adapter will take care of properly splitting and encoding.


### Installation

Start by cloning the github project. Then download and unzip the original [Google vSMS python SDK](https://developers.google.com/business-communications/verified-sms/samples) in the `kannel-vsms` directory. You will end up with a subdirectory called `vsms-python-client-v1`, and a softlink to it named `vsms_python_client_v1` (underscores instead of dashes). A few name qualifiers are needed in the vSMS library:

In `vsms-python-client-v1/verified_sms_hashing_library/__init__.py` add prefixes for the library names:
```
    from vsms_python_client_v1.verified_sms_hashing_library import verified_sms_hash_generator
    from vsms_python_client_v1.verified_sms_hashing_library import string_sanitizer
    from vsms_python_client_v1.verified_sms_hashing_library import url_finder
```

In `vsms-python-client-v1/verified_sms_client_library/verified_sms_service_client.py `also add the prefix for the library name:
```
    from vsms_python_client_v1.verified_sms_hashing_library.verified_sms_hash_generator import VerifiedSmsHashGenerator
```

Before starting the app, you also need to `pip install` the dependencies. The kannel adapter's dependencies are listed in the `requirements.txt` file. The vSMS SDK will come with its own list of dependencies - so check the `requirements.txt` file that it comes with as well.


### Configuration

The main application web server is `kannel_adapter.py`. All the configuration items are global variables in the `config.py` file. For testing purposes, you can run the application from the command line; it will bind to localhost, port 13001, and can be invoked with curl commands like 
```
curl -s http://localhost:13001/cgi-bin/sendsms
```
Obviously, a script from the command line would only be able to process one http request at a time. In a production environment you would use it with a real web server front-end, like Apache + mod_python, or Nginx + uwsgi.

The Google vSMS service requires either an access key or a credentials file, so you would either have to uncomment and set `VSMS_AUTH_APIKEY`, or you would have to save your credentials file as `credentials.json` in the application directory. 

Agent data (the agent keypair, and the origination numbers registered with the vSMS service) is stored as either JSON files in the `agents/` subdirectory, or made available from an external web service. The agent data is cached in memory at application start. Caching can be optionally disabled.

One other decision you would have to make is whether you want to send a text message at all, in case there's something wrong with uploading the vSMS hash first. If verifications were successful before, a message received without proper verification is displayed with a question mark and a warning on the destination device, which may create confusion and doubts. Whether the message should still be sent is depending on each agent's use case, but you may globally control this with the `SEND_UNVERIFIED` variable. Also, whether you want to entirely block messages from origination numbers that are not registered, can be controlled from the `BLOCK_UNREGISTERED` variable.

The adapter logs, by default, in the system log, on log facility 6. Use your syslog settings to redirect the logging to a file or service.


### Operation

After registering a vSMS agent with Google, you will have to generate a keypair for that agent. You do this with the `vsms_agent.py` script, submitting the agent name, and a list of origination phone numbers and /or shortcodes they registered for:
```
    ./vsms_agent.py agent_id orig_num orig_num …
```

You can use the same command every time you want to refresh the agent's keypair, or make changes to the list of registered origination numbers. If you use JSON files to store the agents information, make sure the storage directory is shared across all hosts that run the kannel adapter app. You will need to perform a rolling restart of all your `kannel_adapter` app instances, for the changes to become effective.


