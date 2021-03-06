# -*- coding: utf-8 -*-

import ConfigParser
import logging
import logging.config
import random
import math
import base64
import time
import pymongo
from pymongo import MongoClient
import ujson as json

_LOGGER_NAME = "f6a_tw_backend"
logger = None
config = {}

_mongo_map = {
    'lock': 'lock',
    'f6a_tw_backend': 'f6a_tw_backend',
    'f6a_tw_backend2': 'f6a_tw_backend',
    'f6a_tw_backend3': 'f6a_tw_backend',
    'f6a_tw_backend4': 'f6a_tw_backend',
    'f6a_tw_backend5': 'f6a_tw_backend',
}

_ensure_index = {
    'f6a_tw_backend2': [('name', pymongo.ASCENDING)],
    'f6a_tw_backend3': [('en_name', pymongo.ASCENDING)],
    'f6a_tw_backend4': [('indication', pymongo.ASCENDING)],
    'f6a_tw_backend5': [('permit', pymongo.ASCENDING)],
}

_ensure_unique_index = {
    'lock': [('key', pymongo.ASCENDING)],
}

IS_INIT = False


def init(params):
    '''
    params: log_ini_filename
            ini_filename
    '''
    global IS_INIT
    if IS_INIT:
        return

    IS_INIT = True

    _init_logger(params)
    _init_ini_file(params)
    _post_init_config(params)

    _init_mongo()

    logger.warning('config: %s', config)


def _init_logger(params):
    '''logger'''
    global logger
    logger = logging.getLogger(_LOGGER_NAME)

    log_ini_filename = params.get('log_ini_filename', '')
    if not log_ini_filename:
        log_ini_filename = params.get('ini_filename', '')

    if not log_ini_filename:
        return

    logging.config.fileConfig(log_ini_filename, disable_existing_loggers=False)


def _init_ini_file(params):
    '''
    setup f6a_tw_backend:main config
    '''
    global config

    ini_filename = params.get('ini_filename', '')

    section = 'f6a_tw_backend:main'

    config = init_ini_file(ini_filename, section)


def init_ini_file(ini_filename, section):
    '''
    get ini conf from section
    return: config: {key: val} val: json_loaded
    '''
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(ini_filename)
    options = config_parser.options(section)
    config = {option: _init_ini_file_parse_option(option, section, config_parser) for option in options}
    _post_json_config(config)

    return config


def _init_ini_file_parse_option(option, section, config_parser):
    try:
        val = config_parser.get(section, option)
    except Exception as e:
        logger.exception('unable to get option: section: %s option: %s e: %s', section, option, e)
        val = ''
    return val


def _post_json_config(config):
    '''
    try to do json load on value
    '''
    for k, v in config.iteritems():
        if v.__class__.__name__ != 'str':
            continue

        orig_v = v
        try:
            config[k] = json.loads(v)
        except:
            config[k] = orig_v


def _post_init_config(params):
    '''
    add additional parameters into config
    '''
    logger.warning('params: %s', params)

    for (k, v) in params.iteritems():
        if k in config:
            logger.warning('params will be overwrite: key: %s origin: %s new: %s', k, config[k], v)

    config.update(params)


def _init_mongo():
    '''
    initialize mongo
    '''

    _init_mongo_map_core('mongo', config.get('mongo_server_hostname', 'localhost'), config.get('mongo_server', 'test'), _mongo_map, _ensure_index, _ensure_unique_index)


def _init_mongo_map_core(mongo_prefix, mongo_server_hostname, mongo_server, mongo_map, ensure_index_map, ensure_unique_index_map=None):
    if not ensure_unique_index_map:
        ensure_unique_index_map = {}

    mongo_server_url = mongo_prefix + '_MONGO_SERVER_URL'
    mongo_server_idx = mongo_prefix + '_MONGO_SERVER'

    # mongo_server_url
    if mongo_server_url not in config:
        config[mongo_server_url] = "mongodb://" + mongo_server_hostname + "/" + mongo_server

    try:
        if mongo_server_idx not in config:
            config[mongo_server_idx] = MongoClient(config.get(mongo_server_url), use_greenlets=True)[mongo_server]

        for (key, val) in mongo_map.iteritems():
            if key in config:
                logger.warning('key already in config: key: %s config: %s', key, config[key])
                continue

            logger.warning('mongo: %s => %s', key, val)
            config[key] = config.get(mongo_server_idx)[val]
    except Exception as e:
        logger.error('unable to init mongo: mongo_prefix: %s mongo_server_hostname: %s mongo_server: %s e: %s', mongo_prefix, mongo_server_hostname, mongo_server, e)

        for (key, val) in mongo_map.iteritems():
            config[key] = None

    for (key, val) in ensure_index_map.iteritems():
        logger.warning('to ensure_index: key: %s', key)
        try:
            config[key].ensure_index(val, background=True)
        except Exception as e:
            logging.error('unable to ensure_index: key: %s e: %s', key, e)

    for (key, val) in ensure_unique_index_map.iteritems():
        try:
            config[key].ensure_index(val, background=True, unique=True)
        except Exception as e:
            logging.error('unable to ensure unique index: key: %s e: %s', key, e)
