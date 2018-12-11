#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging

from ontbc.parser import add_clean_parser
from ontbc.common import readfq
from ontbc import __author__, __email__, __version__

LOG = logging.getLogger(__name__)


def clean(args):

    for name, seq, qvalue in readfq(args.fastq):

        if qvalue:
            print("@%s\n%s\n+%s" % (name, seq, qvalue))


def main():
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""


version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_clean_parser(parser)
    args = parser.parse_args()
    clean(args)


if __name__ == "__main__":
    main()

