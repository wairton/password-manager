#!/usr/bin/python3

from subprocess import Popen, PIPE
import argparse
import json
import sys
import tempfile
import os
import getpass
import random


PATH = os.path.join(os.environ['HOME'], 'opt', '.store.gpg')


def load():
    # cmd = f"gpg -c --cipher-type=AES256 {PATH}")
    cmd = f"gpg --decrypt --output - {PATH}"
    out, err = Popen(cmd.split(), stdout=PIPE, stderr=PIPE).communicate()
    return json.loads(out.decode())


def find(expr):
    data = load()
    for item in data:
        if expr in item['name']:
            return item
    return None


def to_clipboard(expr):
    os.system(f"echo '{expr}' | xclip -selection clipboard")


def read_entry(name=None):
    entry = {}
    if name:
        entry['name'] = name
    else:
        entry['name'] = input('name: ')
    entry['user'] = input('user: ')
    entry['password'] = getpass.getpass('password: ').strip()
    return entry


def add(entry):
    data = load()
    for d in data:
        if entry['name'] == d['name']:
            raise Exception("FIX")
    data.append(entry)
    store(json.dumps(data))


def update(expr):
    entry = find(expr)
    if entry is None:
        print("Nenhuma entrada para '{}'".format())
        return False
    print("Atualizando {}. User: {}".format(entry['name'], entry['user']))
    data = load()
    updated_entry = read_entry(entry['name'])
    for d in data:
        if d['name'] == updated_entry['name']:
            d['user'] = updated_entry['user']
            d['password'] = updated_entry['password']
    store(json.dumps(data))


def store(data: str):
    cmd = f"gpg -c --output={PATH} --cipher-algo=AES256 --batch --yes"
    data_bytes = bytes(data, encoding='utf-8')
    out, err = Popen(cmd.split(), stdout=PIPE, stderr=PIPE, stdin=PIPE).communicate(data_bytes)
    if err:
        print(err)


def suggest():
    ss = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&()*+,-./:;<=>?@[]^_'
    return ''.join(random.sample(ss, 15))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--find', type=str)
    parser.add_argument('-a', '--add', type=str)
    parser.add_argument('-u', '--update', type=str)
    parser.add_argument('-d', '--delete', type=str)
    parser.add_argument('-s', '--suggest', action='store_true')
    parser.add_argument('--names', action='store_true')
    parser.add_argument('--dump', action='store_true')
    args = parser.parse_args()
    if args.find:
        item = find(args.find)
        if item is None:
            print(f"No password found for '{args.find}'")
        else:
            print(item['name'], item['user'])
            to_clipboard(item['password'])
    elif args.add:
        add(read_entry(args.add))
    elif args.update:
        update(args.update)
    elif args.names:
        print([a['name'] for a in load()])
    elif args.suggest:
        print(suggest())

