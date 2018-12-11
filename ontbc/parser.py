#!/usr/bin/env python
# -*- coding: utf-8 -*-


def add_filter_parser(parser):
    """
    parser for filter tool
    :param parser:
    :return:
    """

    parser.add_argument("--fastq", metavar="FILE", required=True,
                        help=".fastq")
    parser.add_argument("--summary", metavar="FILE", required=False,
                        help="Ont summary file")
    parser.add_argument("--min_score", metavar="NUM", type=float, required=False,
                        help="Minimum number of read Q score. use with --summary")

    parser.add_argument("--fast5", metavar="FILE", required=False, help="fast5 path file")

    filter_group = parser.add_mutually_exclusive_group(required=False)
    filter_group.add_argument("--min_length", metavar="INT", type=int, default=0,
                              help="Minimum number of read length (default: 0).")
    filter_group.add_argument("--max_bases", metavar="INT", type=int,
                              help="Maximum number of total bases.")

    plot_group = parser.add_argument_group(title="Plot arguments")
    plot_group.add_argument("--plot", action="store_true",
                            help="Plot reads distribution")
    plot_group.add_argument("--window", metavar="INT", type=int,
                            default=1000, help="Window to stat (default: 1000).")
    plot_group.add_argument("--xmax", metavar="INT", type=int,
                            default=200000, help="Maximum number of x axis (default: 200000).")
    plot_group.add_argument("--mode", choices=["num", "base"],
                            default="base", help="Type of y axis (default: base).")

    parser.add_argument("--out",
                        default="out", help="out prefix (default: out).")

    return parser


def add_clean_parser(parser):

    parser.add_argument("fastq", metavar="FASTQ",
                        help=".fastq")

    return parser


def add_barcode_parser(parser):

    parser.add_argument("cell", metavar="DIR",
                        help="Directory of the cell")
    parser.add_argument("--barcode", nargs="+", required=True,
                        help="ONT barcodes, BC01-BC12"),
    parser.add_argument("--job_type", choices=["sge", "local"],
                        default="local", help="Job run type (default:local).")
    parser.add_argument("--threads", type=int, metavar="INT",
                        default=1, help="Threads to use (default:1).")
    parser.add_argument("--work_dir", metavar="DIR",
                        default="work", help="Work directory (default: work).")
    parser.add_argument("--out_dir", metavar="DIR",
                        default="out", help="Out directory (default: out).")

    return parser

