from collections import OrderedDict
from datetime import datetime

RECORD_TYPES = {"flat", "deleted", "compressed"}


INNER_HEADER_SCHEMA = {
    "type": "object",
    "properties": OrderedDict([
        ("Version", {
            "type": "string",
            "default": "1.2",
        }),
        ("Type", {  # autofill or specify
            "type": "string",
            "enum": RECORD_TYPES,
        }),
        ("Fetch-Time", {  # record store time
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
        ("Original-Size", {  # data(html) size, autofill
            "type": "number",
        }),
        ("Store-Size", {  # store size, autofill
            "type": "number",
        }),
        ("batchID", {  # batch identity
            "type": "string",
            "minLength": 3,
            "default": '__CHANGE_ME__',
        }),
        ("attach", {
            "type": "string",
        }),
        ("IP-Address", {  # remote host ip
            "type": "string",
            "format": "ipv4",
            "default": "0.0.0.0",
        }),
        ("Spider-Address", {  # spider node identity
            "type": "string",
            "default": "0.0.0.0",
        }),
        ("Digest", {  # can be html md5
            "type": "string",
            "default": "0" * 32,
            "maxLength": 32,
            "minLength": 32,
        }),
        ("User-Agent", {
            "type": "string",
        }),
        ("Fetch-IP", {  # generate page machine ip
            "type": "string",
            "format": "ipv4",
            "default": "0.0.0.0",
        }),
        ("Node-Fetch-Time", {  # real fetch time
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
        ("Error-Reason", {
            "type": "string",
            "format": "error_reaseon",
        }),
    ]),
}


META_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "format": "url",
        },
        "inner_header": INNER_HEADER_SCHEMA,
        "http_header": {
            "type": "object"
        },
        "data": {
            "type": "string",
        },
    },
    "required": ["url", "inner_header"],
}
