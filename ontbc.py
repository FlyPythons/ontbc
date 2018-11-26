#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging

from ontbc.filter import add_filter_parser, filter_reads
from ontbc.barcode import add_barcode_args, barcode

from ontbc import __author__, __version__, __email__

LOG = logging.getLogger(__name__)


def add_ontbc_parser(parser):

    subparsers = parser.add_subparsers(
        title='command',
        dest='commands')
    subparsers.required = True

    filter_parser = subparsers.add_parser('filter', help="filter records")
    filter_parser = add_filter_parser(filter_parser)
    filter_parser.set_defaults(func=filter_reads)

    barcode_parser = subparsers.add_parser('barcode', help="barcoding")
    barcode_parser = add_barcode_args(barcode_parser)
    barcode_parser.set_defaults(func=barcode)

    return parser


def main():
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
ONT barcode tools

version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_ontbc_parser(parser)
    args = parser.parse_args()

    args.func(args)

    return parser.parse_args()


if __name__ == "__main__":
    main()

