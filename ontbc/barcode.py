#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
import argparse
import logging
from tarfile import TarFile

from thirdparty.dagflow import ParallelTask, Task, DAG, do_dag
from ontbc.common import mkdir, touch, read_tsv
from ontbc.parser import add_barcode_parser
from ontbc.config import PORECHOP_BIN, QUEUE
from ontbc import __file__, __version__, __email__, __author__


LOG = logging.getLogger(__name__)


def read_tar(file):

    a = os.path.dirname(file)

    return [os.path.join(a, i) for i in TarFile(file).getnames()]


def scan_cell(cell):

    fastqs = []
    summarys = []
    fast5s = []

    for root, dirs, files in os.walk(cell, followlinks=True, topdown=False):

        for name in files:
            path = os.path.join(root, name)
            if name.endswith(".fastq"):
                fastqs.append(path)
            elif name.endswith(".txt"):
                summarys.append(path)
            elif name.endswith(".fast5"):
                fast5s.append(path)
            elif name.endswith(".tar"):
                fast5s += read_tar(path)
            else:
                pass

    return fastqs, summarys, fast5s


def create_porechop_tasks(cell, barcodes, job_type, work_dir, out_dir):

    LOG.info("find fastq, summary and fast5 files in %r" % cell)

    fastq_fofn = os.path.join(work_dir, "fastq.fofn")
    summary_fofn = os.path.join(work_dir, "summary.fofn")
    fast5_fofn = os.path.join(work_dir, "fast5.fofn")
    find_done = os.path.join(work_dir, "find_done")

    if not os.path.exists(find_done):
        fastqs, summarys, fast5s = scan_cell(cell)

        for i, j in zip([fastq_fofn, summary_fofn, fast5_fofn], [fastqs, summarys, fast5s]):
            with open(i, "w") as fh:
                fh.write("%s\n" % "\n".join(j))

        del fastqs, summarys, fast5s
        touch(find_done)

    fastqs = [i[0] for i in read_tsv(fastq_fofn)]
    summarys = [i[0] for i in read_tsv(summary_fofn)]
    fast5s = [i[0] for i in read_tsv(fast5_fofn)]
    LOG.info("%s fastq, %s summary and %s fast5 files found" % (len(fastqs), len(summarys), len(fast5s)))

    del summarys, fast5s

    if job_type == "local":
        _option = ""
    else:
        _option = "-q %s" % ",".join(QUEUE)

    tasks = ParallelTask(
        id="bc",
        work_dir="%s/{id}" % work_dir,
        type=job_type,
        option=_option,
        script="""
{ontbc}/ontbc.py clean {{fastq}} > clean.fastq
{porechop}/porechop-runner.py -i clean.fastq -b . -t 1 --verbosity 2 --no_split > porechop.log
rm -rf clean.fastq
""".format(
            porechop=PORECHOP_BIN,
            ontbc=os.path.join(os.path.dirname(__file__), "..")
        ),
        fastq=fastqs,
    )

    summary = os.path.join(work_dir, "all.summary.txt")

    join_summary = Task(
        id="join_summary",
        work_dir=work_dir,
        type=job_type,
        script="""
less {summary} | xargs cat - > all.summary.txt
""".format(
            summary=summary_fofn
        ),
    )

    join_tasks = ParallelTask(
        id="join",
        work_dir=work_dir,
        type=job_type,
        script="""
mkdir -p {out}/{{barcode}}

if [ ! -e {{barcode}}_cat_done ]; then
    cat */{{barcode}}.fastq > {out}/{{barcode}}/{{barcode}}.fastq
    touch {{barcode}}_cat_done
fi

rm -rf */{{barcode}}.fastq

cd {out}/{{barcode}}
{ontbc}/ontbc.py filter --fastq {{barcode}}.fastq --summary {summary} --fast5 {fast5} \\
  --min_score -100 --min_length 0 --out {{barcode}}
rm {{barcode}}.filtered.fastq
mv {{barcode}}.filtered.summary.txt {{barcode}}.summary.txt
""".format(
            summary=summary,
            ontbc=os.path.join(os.path.dirname(__file__), ".."),
            fast5=fast5_fofn,
            out=out_dir
        ),
        barcode=barcodes
    )

    for i in join_tasks:
        i.set_upstream(*tasks)
        i.set_upstream(join_summary)

    return tasks, join_tasks, join_summary


def run_porechop(cell, barcodes, job_type, threads, work_dir, out_dir):

    assert os.path.isdir(cell), "%r not exist" % cell

    out_dir = mkdir(out_dir)
    work_dir = mkdir(work_dir)

    tasks, join_tasks, join_summary = create_porechop_tasks(
        cell=cell,
        barcodes=barcodes,
        job_type=job_type,
        work_dir=work_dir,
        out_dir=out_dir
    )

    dag = DAG("porechop")

    dag.add_task(*tasks)
    dag.add_task(join_summary)
    dag.add_task(*join_tasks)

    do_dag(dag, concurrent_tasks=threads, refresh_time=30)


def barcode(args):

    run_porechop(
        cell=args.cell,
        barcodes=args.barcode,
        job_type=args.job_type,
        threads=args.threads,
        work_dir=args.work_dir,
        out_dir=args.out_dir
    )


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

    parser = add_barcode_parser(parser)
    args = parser.parse_args()
    barcode(args)


if __name__ == "__main__":
    main()

