import sys
from argparse import ArgumentParser
from typing import List, Sequence, Tuple

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
    bases = []
    with open(snps, "r") as ifs:
        for line in ifs.readlines():
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


def main(reference: str, snps: str, output: str) -> int:
    rv = 0
    # noinspection PyBroadException
    try:
        print(reference, snps, output)

        header, sequence = read_reference(reference)
        check_reference_header(header)
        bases = read_snps(snps)
        update_sequence(sequence, bases)
        write_alternate(header, sequence, output)
    except Exception as e:
        rv = 1

    return rv


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--reference", "-r", type=str, help="Reference alleles file")
    parser.add_argument("--snps", "-s", type=str, help="Single nucleotide polymorphisms file")
    parser.add_argument("output", type=str, optional=True, help="Alternative output file")
    args = parser.parse_args(sys.argv[1:])

    sys.exit(main(args.reference, args.snps, args.output))
