#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
library for common functions
"""

import os.path
import logging


LOG = logging.getLogger(__name__)


def read_tsv(file, sep=None):
    """
    read file separated with sep
    :param file: filename
    :param sep: separator
    :return: value list
    """

    for line in open(file):
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        yield line.split(sep)


def readfq(file):  # this is a generator function
    """
    modified from "https://github.com/lh3/readfq"
    :param file: filename
    :return:
    """
    if file.endswith(".gz"):
        fp = gzip.open(file)
    elif file.endswith(".fastq") or file.endswith(".fq"):
        fp = open(file)
    else:
        raise Exception("%r file format error" % file)

    last = None # this is a buffer keeping the last unprocessed line
    while True: # mimic closure; is it a bad idea?
        if not last: # the first record or a record following a fastq
            for l in fp: # search for the start of the next record
                if l[0] in '>@': # fasta/q header line
                    last = l[:-1] # save this line
                    break
        if not last: break
        name, seqs, last = last[1:].partition(" ")[0], [], None
        for l in fp: # read the sequence
            if l[0] in '@+':
                last = l[:-1]
                break
            seqs.append(l[:-1])
        if not last or last[0] != '+': # this is a fasta record
            yield name, ''.join(seqs), None # yield a fasta record
            if not last: break
        else: # this is a fastq record
            seq, leng, seqs = ''.join(seqs), 0, []
            for l in fp: # read the quality
                seqs.append(l[:-1])
                leng += len(l) - 1
                if leng >= len(seq): # have read enough quality
                    last = None
                    yield name, seq, ''.join(seqs); # yield a fastq record
                    break
            if last: # reach EOF before reading enough quality
                yield name, seq, None # yield a fasta record instead
                break



def n50(lengths):
    """
    return N50 of lengths
    :param lengths: a list of length
    :return:
    """
    assert lengths, "lengths %r is empty" % lengths

    sum_length = sum(lengths)
    accu_len = 0

    for i in sorted(lengths, reverse=True):
        accu_len += i

        if accu_len >= sum_length*50/100:
            return i

    return i


def link(source, target, force=False):
    """
    link -s
    :param source:
    :param target:
    :param force:
    :return:
    """
    source = check_paths(source)

    # for link -sf
    if os.path.exists(target):
        if force:
            os.remove(target)
        else:
            raise Exception("%r has been exist" % target)

    LOG.info("ln -s {source} {target}".format(**locals()))
    os.symlink(source, target)

    return os.path.abspath(target)


def check_path(path):

    path = os.path.abspath(path)

    if not os.path.exists(path):
        msg = "File not found '{path}'".format(**locals())
        LOG.error(msg)
        raise Exception(msg)

    return path


def check_paths(obj):
    """
    check the existence of paths
    :param obj:
    :return: abs paths
    """

    if isinstance(obj, list):
        r = []
        for path in obj:
            r.append(check_path(path))

        return r
    else:
        return check_path(obj)


def cd(newdir):
    """
    from FALCON_KIT
    :param newdir:
    :return:
    """
    newdir = os.path.abspath(newdir)
    prevdir = os.getcwd()
    LOG.debug('CD: %r <- %r' % (newdir, prevdir))
    os.chdir(os.path.expanduser(newdir))
    return newdir


def mkdir(d):
    """
    from FALCON_KIT
    :param d:
    :return:
    """
    d = os.path.abspath(d)
    if not os.path.isdir(d):
        LOG.debug('mkdir {!r}'.format(d))
        os.makedirs(d)
    else:
        LOG.debug('mkdir {!r}, {!r} exist'.format(d, d))

    return d


def touch(*paths):
    """
    touch a file.
    from FALCON_KIT
    """

    for path in paths:
        if os.path.exists(path):
            os.utime(path, None)
        else:
            open(path, 'a').close()
            LOG.debug('touch {!r}'.format(path))
