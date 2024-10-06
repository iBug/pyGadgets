#!/usr/bin/python3

import hashlib
import hmac
import json
import logging
import os
import requests
import traceback
import sys

from v2ex import V2ex


def sign(v2ex):
    try:
        balance = v2ex.get_money()
        last = v2ex.get_last()
        v2ex.save_cookie()
        return True, {
            'balance': balance,
            'last': last,
        }
    except KeyError:
        traceback.print_exc()
        return False, 'KeyError, please check your config file.'
    except IndexError:
        return False, 'Please check your username and password.'
    except Exception as e:
        return False, f'{e.__class__.__name__}: {e}'


def visit(v2ex, count=1):
    try:
        visited = v2ex.visit(count, sleep=2)
        return True, {'visited': visited}
    except KeyError:
        traceback.print_exc()
        return False, 'KeyError, please check your config file.'
    except IndexError:
        return False, 'Please check your username and password.'
    except Exception as e:
        return False, f'{e.__class__.__name__}: {e}'


def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    logging.basicConfig(
        filename='run.log',
        level='INFO',
        format='%(asctime)s [%(levelname)s] %(message)s')

    if len(sys.argv) == 1:
        v2ex = V2ex("cookie.txt")
        sign(v2ex)
        return
    elif sys.argv[1] == "sign":
        if len(sys.argv) > 2:
            files = sys.argv[2:]
        else:
            files = ["cookie.txt"]
        for file in files:
            v2ex = V2ex(file)
            sign(v2ex)
        return
    elif sys.argv[1] == "visit":
        filename = sys.argv[2] if len(sys.argv) > 2 else "cookie.txt"
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        v2ex = V2ex(filename)
        visit(v2ex, count)
        return
    raise ValueError(f"Invalid command: {sys.argv[1]}")


if __name__ == '__main__':
    main()
