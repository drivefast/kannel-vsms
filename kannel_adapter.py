# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import random
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
   
    # parse the original query string (the bottle parser is a little greedy)
    msg_urlencoded = ""
    query_tuples = []
    for p in bottle.request.query_string.split("&"):
        if p.startswith("text="):
            msg_urlencoded = p[5:]
        elif p.startswith("text=") or p.startswith("coding="):
            pass
        else:
            query_tuples.append(p)
    orig = bottle.request.query.get('from')
    dest = bottle.request.query.get('to')

    msg_bytes = urllib.parse.unquote_to_bytes(msg_urlencoded)
    log.debug("{} -> {} message bytes: {}".format(orig, dest, msg_bytes))

    msg = None
    # attempt reconstructing the message into several possible SMS-compatible encodings
    for encoding in [ 'gsm0338', 'utf_8', 'utf_16_be' ]:
        try:
            msg = msg_bytes.decode(encoding)
            log.debug("{} -> {} message string ({} encoded): {}"
                .format(orig, dest, encoding, msg)
            )
            break
        except Exception:
            continue

    if msg is not None:

        rq_encoding = "utf_8" if smsutil.is_valid_gsm(msg) else "utf_16_be"
        sms_encoding = "0" if smsutil.is_valid_gsm(msg) else "2"

        # post full message vSMS hash first
        log.debug("{} -> {} hashing string: '{}'".format(orig, dest, msg))
        if not vsms_post_message_hash(orig, dest, msg):
            # message hash not posted properly, and either the agent or the 
            # global settings prevent non-verified SMS messages to be sent
            bottle.response.status = 412
            return

        sms = smsutil.split(msg)
        log.debug("{} -> {} split: {} parts".format(orig, dest, len(sms.parts)))
        if len(sms.parts) > 1:
            udh_id = random.randint(0, 255)
            for pn in range(0, len(sms.parts)):
                # send vSMS hash of the part
                log.debug("{} -> {} hashing part: '{}'".format(orig, dest, sms.parts[pn].content))
                if not vsms_post_message_hash(orig, dest, sms.parts[pn].content):
                    bottle.response.status = 412
                    return
                # now send the part itself
                log.debug("{} -> {} transmitting part: '{}'"
                    .format(orig, dest, sms.parts[pn].content.encode(rq_encoding))
                )
                kannel_rp = requests.get(KANNEL_URL + "?" + 
                    "&".join(query_tuples) + 
                    "&udh=" + "%05%00%03%{:02X}%{:02X}%{:02X}".format(udh_id, len(sms.parts), 1 + pn) +
                    "&text=" + urllib.parse.quote(sms.parts[pn].content.encode(rq_encoding)) + 
                    "&coding=" + sms_encoding
                )
                if kannel_rp.status_code < 200 or kannel_rp.status_code >= 400:
                    break
        else:
            # message fits in one single PDU, just send as SMS
            log.debug("{} -> {} transmitting string: '{}'".format(orig, dest, msg))
            kannel_rp = requests.get(KANNEL_URL + "?" + 
                "&".join(query_tuples) + 
                "&text=" + urllib.parse.quote(msg.encode(rq_encoding)) +
                "&coding=" + sms_encoding
            )

        bottle.response.status = kannel_rp.status_code
        bottle.response.set_header("Content-Type", kannel_rp.headers['Content-Type'])
        return kannel_rp.content

    # something happened with identifying the request parts, 
    # try forwarding to kannel unaltered
    log.info("{} -> {} message could not be decoded".format(orig, dest))
    kannel_rp = requests.get(KANNEL_URL + "?" + bottle.request.query_string)
    bottle.response.status = kannel_rp.status_code
    bottle.response.set_header("Content-Type", kannel_rp.headers['Content-Type'])
    return kannel_rp.content


@bottle.post(LISTEN_URL_PATH)
def send_message_as_post():

    xk_headers = {}
    rq_headers = dict(bottle.request.headers)
    for h in rq_headers.keys():
        if h.lower().startswith("x-kannel-"):
            xk_headers[h] = rq_headers[h]
    orig = bottle.request.headers.get('X-Kannel-From')
    dest = bottle.request.headers.get('X-Kannel-To')

    msg_bytes = bottle.request.body.read()
    log.debug("{} -> {} message bytes: {}".format(orig, dest, msg_bytes))

    msg = None
    # attempt decoding the message content
    for encoding in [ 'gsm0338', 'utf_8', 'utf_16_be' ]:
        try:
            msg = msg_bytes.decode(encoding)
            log.debug("{} -> {} message string ({} encoded): {}"
                .format(orig, dest, encoding, msg)
            )
            break
        except Exception:
            continue

    if msg is not None:

        rq_encoding = "utf_8" if smsutil.is_valid_gsm(msg) else "utf_16_be"
        xk_headers['X-Kannel-Coding'] = "0" if smsutil.is_valid_gsm(msg) else "2"

        # post full message vSMS hash first
        log.debug("{} -> {} hashing string: '{}'".format(orig, dest, msg))
        if not vsms_post_message_hash(orig, dest, msg):
            # message hash not posted properly, and either the agent or the 
            # global settings prevent non-verified SMS messages to be sent
            bottle.response.status = 412
            return

        sms = smsutil.split(msg)
        log.debug("{} -> {} split: {} parts".format(orig, dest, len(sms.parts)))
        if len(sms.parts) > 1:
            udh_id = random.randint(0, 255)
            for pn in range(0, len(sms.parts)):
                # send vSMS hash of the part
                log.debug("{} -> {} hashing part: '{}'".format(orig, dest, sms.parts[pn].content))
                if not vsms_post_message_hash(orig, dest, sms.parts[pn].content):
                    bottle.response.status = 412
                    return
                # now send the part itself
                log.debug("{} -> {} transmitting part: '{}'"
                    .format(orig, dest, sms.parts[pn].content.encode(rq_encoding))
                )
                xk_headers['X-Kannel-UDH'] = "%05%00%03%{:02X}%{:02X}%{:02X}"\
                    .format(udh_id, len(sms.parts), 1 + pn)
                kannel_rp = requests.post(KANNEL_URL,
                    headers=xk_headers,
                    data=sms.parts[pn].content.encode(rq_encoding)
                )
                if kannel_rp.status_code < 200 or kannel_rp.status_code >= 400:
                    break
        else:
            # message fits in one single PDU, just send as SMS
            log.debug("{} -> {} transmitting string: '{}'".format(orig, dest, msg))
            kannel_rp = requests.post(KANNEL_URL, 
                headers=xk_headers, 
                data=msg.encode(rq_encoding)
            )

        bottle.response.status = kannel_rp.status_code
        bottle.response.set_header("Content-Type", kannel_rp.headers['Content-Type'])
        return kannel_rp.content

    # try forwarding request to kannel unaltered
    log.info("{} -> {} message could not be decoded".format(orig, dest))
    kannel_rp = requests.get(KANNEL_URL, headers=xk_headers, data=msg_bytes)
    bottle.response.status = kannel_rp.status_code
    bottle.response.set_header("Content-Type", kannel_rp.headers['Content-Type'])
    return kannel_rp.content


def vsms_post_message_hash(orig_num, dest_num, msg_string):

    agent = None
    try:
        agent_id = AGENT_FOR[orig_num]
        agent = AGENTS[agent_id]
    except Exception as e:
        log.info("{} -> {} found no valid agent for sender: {}".format(orig_num, dest_num, e))
        return SEND_UNVERIFIED

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
        log.info("[{}] {} -> {} vSMS hash posted; server says: '{}'"
            .format(agent_id, orig_num, dest_num, vsms_rp)
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


