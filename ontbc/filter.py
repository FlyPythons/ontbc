#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging
import os.path

from ontbc.parser import add_filter_parser
from ontbc.common import read_tsv, n50, readfq
from ontbc import __author__, __email__, __version__


LOG = logging.getLogger(__name__)


def get_summary(summary):
    """
    read summary file into dict
    :param summary: summary file
    :return: dict
    """
    r = {}
    LOG.info("Parse ont summary from %r" % summary)

    for record in read_tsv(summary, sep=None):
        r[record[1]] = record

    return r


def get_fast5(fast5):
    """
    read fast5 file into dict
    :param fast5: summary file
    :return: dict
    """
    r = {}
    LOG.info("Parse fast5 from %r" % fast5)

    for record in read_tsv(fast5, sep="\t"):
        r[os.path.basename(record[0])] = record[0]

    return r


def get_length(file):
    """
    get the length and id of reads
    :param file: fastq file
    :return: id and length dict
    """
    r = {}
    LOG.info("Get sequence length")
    for name, seq, qual in readfq(file):
        r[name] = len(seq)

    return r


def _filter_reads(length_dict, summary_dict, min_score, min_length, max_bases):
    """

    :param length_dict:
    :param summary_dict:
    :param min_score:
    :param min_length:
    :param max_bases:
    :return:
    """
    r = {}

    sum_bases = 0

    assert min_score and summary_dict or not min_score and not summary_dict, "--min_score and --summary must be defined"

    if min_length:
        LOG.info("Filter sequences with score >= %s, length >= %s" % (min_score, min_length))
    else:
        LOG.info("Filter sequences with score >= %s, total bases >= %s" % (min_score, max_bases))

    if summary_dict:
        score_index = summary_dict["read_id"].index("mean_qscore_template")

        for k, v in sorted(length_dict.items(), key=lambda d: d[1], reverse=True):

            _id = k.split()[0]
            if _id not in summary_dict:
                LOG.warning("read %r not in summary" % k)
                continue

            if float(summary_dict[_id][score_index]) < min_score:  # filter by qscore
                LOG.info("read %r score < %s" % (_id, min_score))
                continue

            if v < min_length:  # filter by length
                break

            sum_bases += v
            r[k] = v

            if max_bases and sum_bases > max_bases:  # filter by total bases
                break
    else:
        for k, v in sorted(length_dict.items(), key=lambda d: d[1], reverse=True):

            if v < min_length:  # filter by length
                break

            sum_bases += v
            r[k] = v

            if max_bases and sum_bases > max_bases:  # filter by total bases
                break

    return r

"""
def plot_reads_number(lengths, window, x_max, x_min=0, mode="num"):

    num = int((x_max - x_min) / window) + 1
    x = [x_min + i * window for i in range(num)]
    y = []
    info = {i: [] for i in x}

    for n in lengths:
        if n in info:
            info[n].append(n)
            continue
        pos = int(n / window) * window

        if pos in info:
            info[pos].append(n)

    y_num = len(lengths)
    y_sum = sum(lengths)

    for i in x:
        if mode == "base":
            y.append(100.0 * sum(info[i]) / y_sum)
        elif mode == "num":
            y.append(100.0 * len(info[i]) / y_num)
        else:
            raise Exception("Unknown mode %r" % mode)

    return [i + window / 2 for i in x], y


def _plot(plt, lengths, window, x_max, mode, out):

    LOG.info("Plot reads distribution to %r" % out)
    x, y = plot_reads_number(lengths, window, x_max, x_min=0, mode=mode)

    fig, ax = plt.subplots(figsize=(8, 6), )
    plt.bar(x, y, width=window, linewidth=0.5, edgecolor=None)

    if mode == "base":
        y_label = "% Bases"
    elif mode == "num":
        y_label = "% Number"
    else:
        raise Exception()

    plt.ylabel(y_label, weight="bold", fontsize=10)
    plt.xlabel('Read Length (bp)', weight="bold", fontsize=10)
    plt.xticks()

    plt.savefig("%s.png" % out, dpi=600)
"""


def filter_reads(args):
    """

    :param args:
    :return:
    """
    raw_length_dict = get_length(args.fastq)

    if args.summary:
        summary_dict = get_summary(args.summary)
    else:
        summary_dict = {}

    filter_length_dict = _filter_reads(
        length_dict=raw_length_dict,
        summary_dict=summary_dict,
        min_score=args.min_score,
        min_length=args.min_length,
        max_bases=args.max_bases
    )

    raw_lengths = raw_length_dict.values()
    filter_lengths = filter_length_dict.values()

    """
    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib import pyplot as plt

        _plot(plt, lengths=raw_lengths,
              window=args.window,
              x_max=args.xmax,
              mode=args.mode,
              out=args.out+".raw_reads")

        _plot(plt, lengths=filter_lengths,
              window=args.window,
              x_max=args.xmax,
              mode=args.mode,
              out=args.out + ".filter_reads")
    """

    LOG.info("Output results")

    out_stat = open("%s.reads_stat.tsv" % args.out, "w")
    out_stat.write("""\
#Type\tBases (bp)\tReads number\tReads mean length (bp)\tReads N50 (bp)\tLongest Reads (bp)
Raw Reads\t{0:,}\t{1:,}\t{2:,}\t{3:,}\t{4:,}
Filtered Reads\t{5:,}\t{6:,}\t{7:,}\t{8:,}\t{9:,}
""".format(
        sum(raw_lengths), len(raw_lengths), int(sum(raw_lengths) / len(raw_lengths)), n50(raw_lengths),
        max(raw_lengths),
        sum(filter_lengths), len(filter_lengths), int(sum(filter_lengths) / len(filter_lengths)), n50(filter_lengths),
        max(filter_lengths),
    ))

    out_stat.close()

    if args.fast5:
        assert os.path.exists(args.fast5)
        fast5 = get_fast5(args.fast5)

    read_out = []

    out_fastq = open("%s.filtered.fastq" % args.out, "w")

    if summary_dict:
        out_summary = open("%s.filtered.summary.txt" % args.out, "w")
        out_summary.write("\t".join(summary_dict["read_id"]) + "\n")

        for name, seq, qual in readfq(args.fastq):

            if name in filter_length_dict:
                _id = name.split()[0]
                out_fastq.write("@%s\n%s\n+\n%s\n" % (name, seq, qual))
                out_summary.write("\t".join(summary_dict[_id])+"\n")

                if args.fast5:
                    read_out.append("%s\n" % fast5[summary_dict[_id][0]])

        out_summary.close()
    else:
        for name, seq, qual in readfq(args.fastq):
            if name in filter_length_dict:
                out_fastq.write("@%s\n%s\n+\n%s\n" % (name, seq, qual))

    out_fastq.close()

    if read_out:
        with open("%s.fast5.list" % args.out, "w") as fh:
            fh.write("".join(read_out))


def main():
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Filter ont reads with length or qscore

version: %s
contact:  %s <%s>\
    """ % (__version__, " ".join(__author__), __email__))

    parser = add_filter_parser(parser)
    args = parser.parse_args()
    filter_reads(args)


if __name__ == "__main__":
    main()

