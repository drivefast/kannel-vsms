# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import json
import base64
import urllib.parse
import smsutil
import bottle
import requests

import traceback

from vsms_python_client_v1.verified_sms_client_library.verified_sms_service_client import VerifiedSmsServiceClient

from config import *
from vsms_agent import set_agent_key, load_agents


@bottle.get(LISTEN_URL_PATH)
def send_message_as_get():
   
    msg = None
    for p in bottle.request.query_string.split("&"):
        if p.startswith("text="):
            msg = p[5:]
            break
    udh = bottle.request.query.get('udh', "")
    if send_message_hash(
        bottle.request.query.get('from'),
        bottle.request.query.get('to'),
        bottle.request.query.get('coding', "1" if udh else "0"),
        urllib.parse.unquote_to_bytes(msg), 
        urllib.parse.unquote_to_bytes(udh)
    ):
        kannel_rp = requests.get(KANNEL_URL + "?" + bottle.request.query_string)
        bottle.response.status = kannel_rp.status_code
        bottle.response.set_header("Content-Type", kannel_rp.headers['Content-Type'])
        return kannel_rp.content
    else:
        bottle.response.status = 412
        return


@bottle.post(LISTEN_URL_PATH)
def send_message_as_post():

    raw_content = bottle.request.body.read()
    udh = bottle.request.headers.get('X-Kannel-UDH', "")
    if send_message_hash(
        bottle.request.headers.get('X-Kannel-From'),
        bottle.request.headers['X-Kannel-To'],
        bottle.request.headers.get('X-Kannel-Coding', "1" if udh else "0"),
        raw_content,
        urllib.parse.unquote_to_bytes(udh)
    ):
        rq_headers = dict(bottle.request.headers)
        kannel_headers = {}
        for h in rq_headers.keys():
            if h.lower().startswith("x-kannel-"):
                kannel_headers[h] = rq_headers[h]
        kannel_headers['Content-Type'] = rq_headers['Content-Type']
        rp = requests.post(KANNEL_URL, headers=kannel_headers, data=raw_content)
        bottle.response.status = rp.status_code
        bottle.response.set_header("Content-Type", rp.headers['Content-Type'])
        return rp.content
    else:
        bottle.response.status = 412
        return


def send_message_hash(orig_num, dest_num, coding, msg_bytes, udh_bytes=""):

    agent = None
    try:
        agent_id = AGENT_FOR[orig_num]
        agent = AGENTS[agent_id]
    except Exception as e:
        log.debug("[] {} -> {} found no valid agent for sender: {}".format(orig_num, dest_num, e))
        return SEND_UNVERIFIED

    if msg_bytes is None:
        log.warning("[{}] {} -> {} no message content".format(agent_id, orig_num, dest_num))
        return agent.get('send_unverified', SEND_UNVERIFIED)

    msg_bytes = udh_bytes + msg_bytes
    if coding == "0":
        msg_string = smsutil.decode(msg_bytes)
    elif coding == "1":
        msg_string = msg_bytes.decode('utf-8')
    elif coding == "2":
        msg_string = smsutil.decode(msg_bytes, encoding='utf_16_be')
    else:
        log.warning("[{}] {} -> {} bad coding '{}'".format(agent_id, orig_num, dest_num, coding))
        return agent.get('send_unverified', SEND_UNVERIFIED)
    log.debug("[{}] {} -> {} sending hash for message '{}' with{} UDH"
        .format(agent_id, orig_num, dest_num, msg_string, "" if udh_bytes else "out")
    )

    try:
        vsms_client = \
            VerifiedSmsServiceClient(api_key=VSMS_AUTH_APIKEY) \
                if VSMS_AUTH_APIKEY is not None else \
            VerifiedSmsServiceClient(service_account_as_json=VSMS_AUTH_SERVICEACCOUNT)
        if DEBUG_MODE:
            log.debug("[{}] key on vSMS server: '{}' key on local server: '{}'"
                .format(agent_id, vsms_client.get_agent_public_key(agent_id), agent['vsms_keys']['public'])
            )
        vsms_rp = vsms_client.create_hashes(
            agent_id, 
            { "+" + dest_num.replace("+", ""): msg_string },
            base64.b64decode(agent['vsms_keys']['private']),
            debug_mode=DEBUG_MODE
        )
        log.debug("[{}] {} -> {} vSMS hash of '{}' posted; server says: '{}'"
            .format(agent_id, orig_num, dest_num, msg_string, vsms_rp)
        )
    except Exception as e:
        log.warning("[{}] {} -> {} vSMS failed: {}".format(agent_id, orig_num, dest_num, traceback.format_exc()))
        return agent.get('send_unverified', SEND_UNVERIFIED)

    return True



if __name__ == '__main__':
    load_config()
    (AGENT_FOR, AGENTS) = load_agents()
#    print(AGENT_FOR, AGENTS)
    bottle.run(host=LISTEN_HOST, port=LISTEN_PORT, reloader=True)
else:
    load_config()
    (AGENT_FOR, AGENTS) = load_agents()
    app = application = bottle.default_app()


