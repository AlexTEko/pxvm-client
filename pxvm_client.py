#!/usr/bin/env python3

import requests
import logging
import argparse
import json
import os


def load_config():
    config = None
    for loc in os.curdir, os.path.expanduser("~"):
        try:
            with open(os.path.join(loc, '.pxvm_config.json')) as source:
                try:
                    config = json.load(source)
                except json.decoder.JSONDecodeError:
                    print('Error decoding config')
        except IOError:
            pass

    if not config:
        exit('No config loaded')

    return config


def create_machine(hostname):
    config = load_config()
    if hostname:
        data = dict()
        data.setdefault('hostname', hostname)
    headers = {'Authorization': '{}:{}'.format(config.get('user'), config.get('password'))}
    response = requests.post('{}/api/lxc'.format(config.get('url')), headers=headers, json=data)
    logging.debug(response.json())
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('type', help='type of operation', choices=['create'])
    parser.add_argument('--name', help='hostname of LXC machine')
    parser.add_argument('--log', help='log file. Default is None',
                    action='store', default=None)
    parser.add_argument('--log-format', help='log formating', action='store',
                    default='%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')
    parser.add_argument('--log-level', help='log level. Default is warning',
                    action='store', default='error',
                    choices=['debug', 'info', 'warning', 'error', 'critical'])
    args = parser.parse_args()

    loglevel = getattr(logging, args.log_level.upper())
    logging.basicConfig(filename=args.log, format=args.log_format, level=loglevel)

    result = None

    if args.type == 'create':
        result = create_machine(args.name)
        if result.status_code == 200:
            result = result.json()
            print('Hostname: ', result['config']['hostname'])
            print('IP: ', result['ip'])
