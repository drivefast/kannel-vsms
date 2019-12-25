# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import time
import json
import base64
import requests

from vsms_python_client_v1.verified_sms_client_library.verified_sms_service_client import VerifiedSmsServiceClient
from config import * 

def set_agent_key(agent_id):

    # generate new keypair for agent
    priv_k, pub_k = subprocess.run(["./agent_keys", "agent_id"],
        stdout=subprocess.PIPE, universal_newlines=True
    ).stdout.splitlines()

    try:
        vsms = \
            VerifiedSmsServiceClient(api_key=VSMS_AUTH_APIKEY) \
                if VSMS_AUTH_APIKEY is not None  else \
            VerifiedSmsServiceClient(service_account_as_json=VSMS_AUTH_SERVICEACCOUNT)
        vsms.update_key(agent_id, base64.b64decode(pub_k))
    except Exception as e:
        return "Key update for agent '{}' failed at vSMS service:\n{}".format(agent_id, e)

    # save keypair in local or remote storage
    agent = None
    if AGENT_DATA.startswith("file://"):
        fn = AGENT_DATA.replace("file://", "") + agent_id + ".json"
        try:
            fh = open(fn)
            agent = json.loads(fh.read())
            fh.close()
        except FileNotFoundError:
            agent = { 'id': agent_id }
        agent['vsms_keys'] = { 'private': priv_k, 'public': pub_k, 'ts': time.time() }
        fh = open(fn, "w")
        fh.write(json.dumps(agent))
        fh.close()
    elif AGENT_DATA.startswith("http://") or AGENT_DATA.startswith("https://"):
        agent = {
            'id': agent_id,
            'vsms_keys': { 'private': priv_k, 'public': pub_k, 'ts': time.time() }
        }
        rp = requests.post(AGENT_DATA, auth=AGENT_DATA_AUTH, json=agent)
        if rp.status_code >= 400:
            return "Key update for agent '{}' failed to store with status {}: {}"\
                .format(agent_id, rp.status_code, rp.content)

    return agent


def load_agents():
    if not CACHE_AGENT_DATA:
        return ""

    _AGENT_FOR = {}
    _AGENTS = {}
    if AGENT_DATA.startswith("file://"):
        path = AGENT_DATA.replace("file://", "")
        filenames = list(fn for fn in os.listdir(path) if (
            os.path.isfile(os.path.join(path, fn)) and 
            fn.endswith(".json") and 
            not fn.startswith(".")
        ))
        for fn in filenames:
            with open(path + fn, "r") as fh:
                try:
                    agent = json.loads(fh.read())
                except JSONDecodeError as je:
                    print(fn + " - no JSON content")
                    return None, None
            # process sender IDs that can use this agent
            for si in agent.get('sender_ids', []):
                _AGENT_FOR[si] = agent['id']
            # cache the agent info
            _AGENTS[agent['id']] = agent

    elif AGENT_DATA.startswith("http://") or AGENT_DATA.startswith("https://"):
        rp = requests.get(AGENT_DATA, auth=AGENT_DATA_AUTH)
        if rp.status_code >= 400:
            print("No agents loaded: server returned status {}: {}"
                .format(rp.status_code, rp.content)
            )
            return None, None
        _AGENTS = rp.json()
        for agent_id in _AGENTS.keys():
            for si in _AGENTS[agent_id].get('sender_ids', []):
                _AGENT_FOR[si] = agent_id

    return _AGENT_FOR, _AGENTS


if __name__ == '__main__':
    load_config()
    if len(sys.argv) > 1:
        new_agent = sys.argv[1]
        agent_error = set_agent_key(new_agent)
        if not isinstance(agent_error, dict):
            print(agent_error)
        else:
            print("A new agent key for '" + new_agent + "' has been registered.")
            print("You should now restart all the instances of your proxy server.")
            exit()
    else:
        print("No agent key was changed. Please provide the vSMS agent id as an argument.")

