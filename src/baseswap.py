import glob
import os
import sys
from argparse import ArgumentParser
from typing import List, Optional, Sequence, Tuple

LINE_LENGTH = 60


def read_reference(reference: str) -> Tuple[str, List[str]]:
    with open(reference, "r") as ifs:
        lines = ifs.readlines()
        header = lines[0].strip()
        sequence = []
        for line in lines[1:]:
            sequence += line.strip()
    return header, sequence


def check_reference_header(header: str) -> None:
    if not header.endswith("reference_alleles"):
        raise ValueError("Invalid reference allele header: " + header)


def read_snps(snps: str) -> Sequence[Tuple[int, str]]:
    def _is_header(l):
        return False

    bases = []
    with open(snps, "r") as ifs:
        for line in ifs.readlines():
            if not bases and _is_header(line):  # ignore any header row
                continue
            vals = line.strip().split(" ")
            pos = int(vals[0])
            base = vals[1]
            bases.append((pos, base))
    return bases


def update_sequence(sequence: List[str], snps: Sequence[Tuple[int, str]]) -> None:
    for (pos, base) in snps:
        sequence[pos - 1] = base


def write_alternate(header: str, sequence: List[str], output: str) -> None:
    with open(output, "w") as ofs:
        print(header.replace("reference_alleles", "alternative_alleles"), file=ofs)
        ptr = 0
        while ptr < len(sequence):
            print("".join(sequence[ptr:ptr + LINE_LENGTH]), file=ofs)
            ptr += LINE_LENGTH


def process_conversions(
    directory: Optional[str], reference: Optional[str], snps: Optional[str], output: Optional[str]
) -> int:
    rv = 0
    # should have either directory specified, or both reference/snps, but not both
    if directory:
        if reference or snps:
            raise Exception("Can't specify both directory and reference/snps")
        refs = glob.glob(directory + os.path.sep + "reference_*")
        for r in refs:
            s = os.path.join(os.path.dirname(r), os.path.basename(r).replace("reference", "snps"))
            if os.path.exists(s):
                rv += process_conversion(r, s)
            else:
                raise Exception("Can't find snps for reference: " + ref + "(" + snp + ")")
    elif reference and snps:
        rv = process_conversion(reference, snps, output)
    else:
        raise Exception("Need to specify either directory or both reference/snps")

    return rv


def process_conversion(reference: str, snps: str, output: Optional[str] = None) -> int:
    rv = 0
    # noinspection PyBroadException
    try:
        if not output:
            output = os.path.join(os.path.dirname(reference), os.path.basename(reference) + ".alt")

        header, sequence = read_reference(reference)
        check_reference_header(header)
        bases = read_snps(snps)
        update_sequence(sequence, bases)
        write_alternate(header, sequence, output or k)
    except Exception as e:
        rv = 1
        print(e)

    return rv


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--directory", "-d", type=str, help="Reference alleles/snps directory")
    parser.add_argument("--reference", "-r", type=str, help="Reference alleles file")
    parser.add_argument("--snps", "-s", type=str, help="Single nucleotide polymorphisms file")
    parser.add_argument("output", type=str, nargs="?", help="Alternative output file")
    args = parser.parse_args(sys.argv[1:])

    sys.exit(process_conversions(args.directory, args.reference, args.snps, args.output))
