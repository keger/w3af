#!/usr/bin/env python

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(prog='extract_http_from_log')
    parser.add_argument('log_file', help='The w3af HTTP log file generated by text_file')
    parser.add_argument('id', type=int, help='The HTTP request ID to extract')
    return parser.parse_args()


def extract(log_file, http_request_id):
    spacer = '=' * 40
    end_header = '=' * 117

    inside_request = False
    inside_response = False
    request = ''
    response = ''

    for line in open(log_file):

        request_header = '%sRequest %s - ' % (spacer, http_request_id)
        if line.startswith(request_header):
            inside_request = True
            continue

        request_header = '%sResponse %s - ' % (spacer, http_request_id)
        if line.startswith(request_header):
            inside_request = False
            inside_response = True
            continue

        if line.startswith(end_header) and inside_response:
            break

        if inside_request:
            request += line

        if inside_response:
            response += line

    return request, response


def main(args):
    try:
        request, response = extract(args.log_file, args.id)
    except Exception, e:
        print(e)
        sys.exit(1)

    file('%s.request' % args.id, 'w').write(request)
    file('%s.response' % args.id, 'w').write(response)


if __name__ == '__main__':
    args = parse_args()
    main(args)