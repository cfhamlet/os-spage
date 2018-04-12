from collections import OrderedDict
from datetime import datetime


class RecordTypes(object):
    FLAT       = 'flat'
    DELETED    = 'deleted'
    COMPRESSED = 'compressed'


class InnerHeaderKeys(object):
    VERSION           = 'Version'
    TYPE              = 'Type'
    FETCH_TIME        = 'Fetch-Time'
    ORIGINAL_SIZE     = 'Original-Size'
    STORE_SIZE        = 'Store-Size'
    BATCH_ID          = 'batchID'
    ATTACH            = 'attach'
    IP_ADDRESS        = 'IP-Address'
    SPIDER_ADDRESS    = 'Spider-Address'
    DIGEST            = 'Digest'
    USER_AGENT        = 'User-Agent'
    FETCH_IP          = 'Fetch-IP'
    NODE_FETCH_TIME   = 'Node-Fetch-Time'
    ERROR_REASON      = 'Error-Reason'


INNER_HEADER_SCHEMA = {
    "type": "object",
    "properties": OrderedDict([
        (InnerHeaderKeys.VERSION, {
            "type": "string",
            "default": "1.2",
        }),
        (InnerHeaderKeys.TYPE, {  # autofill or specify
            "type": "string",
            "enum": set([getattr(RecordTypes, i) for i in dir(RecordTypes) if not i.startswith('_')]) ,
        }),
        (InnerHeaderKeys.FETCH_TIME, {  # record store time
            "anyOf": [
                {
                    "type": "datetime",
                },
                {
                    "type": "string",
                    "format": "readable_time"
                },
            ],
            "default": datetime.now,
        }),
        (InnerHeaderKeys.ORIGINAL_SIZE, {  # data(html) size, autofill
            "type": "number",
        }),
        (InnerHeaderKeys.STORE_SIZE, {  # store size, autofill
            "type": "number",
        }),
        (InnerHeaderKeys.BATCH_ID, {  # batch identity
            "type": "string",
            "minLength": 3,
            "default": '__CHANGE_ME__',
        }),
        (InnerHeaderKeys.ATTACH, {
            "type": "string",
        }),
        (InnerHeaderKeys.IP_ADDRESS, {  # remote host ip
            "type": "string",
            "format": "ipv4",
            "default": "0.0.0.0",
        }),
        (InnerHeaderKeys.SPIDER_ADDRESS, {  # spider node identity
            "type": "string",
            "default": "0.0.0.0",
        }),
        (InnerHeaderKeys.DIGEST, {  # can be html md5
            "type": "string",
            "default": "0" * 32,
            "maxLength": 32,
            "minLength": 32,
        }),
        (InnerHeaderKeys.USER_AGENT, {
            "type": "string",
        }),
        (InnerHeaderKeys.FETCH_IP, {  # generate page machine ip
            "type": "string",
            "format": "ipv4",
            "default": "0.0.0.0",
        }),
        (InnerHeaderKeys.NODE_FETCH_TIME, {  # real fetch time
            "anyOf": [
                {
                    "type": "datetime",
                },
                {
                    "type": "string",
                    "format": "readable_time"
                },
            ]
        }),
        (InnerHeaderKeys.ERROR_REASON, {
            "type": "string",
            "format": "error_reaseon",
        }),
    ]),
}

class SpageKeys(object):
    URL          = 'url'
    INNER_HEADER = 'inner_header'
    HTTP_HEADER  = 'http_header'
    DATA         = 'data'


META_SCHEMA = {
    "type": "object",
    "properties": {
        SpageKeys.URL: {
            "type": "string",
            "format": "url",
        },
        SpageKeys.INNER_HEADER: INNER_HEADER_SCHEMA,
        SpageKeys.HTTP_HEADER: {
            "type": "object"
        },
        SpageKeys.DATA: {
            "type": "bytes",
        },
    },
    "required": [SpageKeys.URL, SpageKeys.INNER_HEADER],
}
