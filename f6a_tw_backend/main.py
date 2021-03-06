#!/usr/bin/env python
# -*- coding: utf-8 -*-

from f6a_tw_backend.constants import *

import gevent.monkey; gevent.monkey.patch_all()

from bottle import Bottle, request, response, route, run, post, get, static_file, redirect, HTTPError, view, template

import random
import math
import base64
import time
import ujson as json
import sys
import argparse
from beaker.middleware import SessionMiddleware

from f6a_tw_backend import cfg
from f6a_tw_backend import util

app = Bottle()


@app.get('/')
def dummy():
    return _process_result("1")


def _process_params():
    return dict(request.params)


def _process_json_request():
    return util.json_loads(_process_body_request())


def _process_body_request():
    f = request.body
    f.seek(0)
    return f.read()


def _process_result(the_obj):
    response.set_header('Accept', '*')
    response.set_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Methods', '*')
    response.content_type = 'application/json'
    return util.json_dumps(the_obj)


def _process_mime_result(content_type, content):
    response.set_header('Accept', '*')
    response.set_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Methods', '*')
    response.content_type = content_type
    return content


def parse_args():
    ''' '''
    parser = argparse.ArgumentParser(description='f6a_tw_backend')
    parser.add_argument('-i', '--ini', type=str, required=True, help="ini filename")
    parser.add_argument('-l', '--log_filename', type=str, default='', required=False, help="log filename")
    parser.add_argument('-p', '--port', type=str, required=True, help="port")

    args = parser.parse_args()

    return (S_OK, args)


def _main():
    global app

    (error_code, args) = parse_args()

    cfg.init({"port": args.port, "ini_filename": args.ini, 'log_filename': args.log_filename})

    session_opts = {
        'session.cookie_expires': True,
        'session.encrypt_key': cfg.config.get('session_encrypt_key', '')
        'session.httponly': True,
        'session.timeout': cfg.config.get('session_expire_timestamp', SESSION_EXPIRE_TIMESTAMP)
        'session.type': 'cookie',
        'session.validate_key': True,
    }

    app = SessionMiddleware(app, session_opts)

    run(app, host='0.0.0.0', port=cfg.config.get('port'), server='gevent')


if __name__ == '__main__':
    _main()
