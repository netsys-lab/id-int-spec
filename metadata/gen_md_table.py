#!/usr/bin/python3

import argparse
import itertools
import yaml


parser = argparse.ArgumentParser(description="Format metadata definitions")
parser.add_argument("--input", default="./metadata.yaml", help="Metadata definitions")
parser.add_argument("--tables", default=None, help="Output file for tables ordered by category")
parser.add_argument("--inst-assign", default=None, help="Output file for instruction overview table")
parser.add_argument("--p4", default=None, help="Output file for P4 definitions of the instructions")
args = parser.parse_args()


with open(args.input, 'r') as file:
    defs = yaml.safe_load(file)

if args.tables:
    with open(args.tables, 'w') as f:
        for i, group in enumerate(defs):
            if i > 0:
                f.write("\n")
            f.write(f"### {group['name']}\n\n")
            f.write("Metadatum                       | Inst | Length |   Unit  | Description\n")
            f.write("--------------------------------|-----:|-------:|--------:|-----------------------------------------\n")
            for md in group['metadata']:
                f.write("{name:<32}| 0x{instruction:>02X} | {length:>6} | ".format(**md))
                f.write("{:>7} |".format(md.get('unit', "")))
                if 'brief' in md:
                    f.write(" {}".format(md['brief']))
                f.write("\n")

            details = [md for md in group['metadata'] if md.get('details')]
            if len(details) > 0:
                f.write("\n#### Details\n")
                for md in details:
                    f.write(f"- {md['name']}\n\n")
                    for line in md['details'].split("\n"):
                        f.write(f"  {line}\n")

if args.inst_assign or args.p4:
    flat = [md for group in defs for md in group['metadata']]
    flat.sort(key=lambda md: md['instruction'])

if args.inst_assign:
    with open(args.inst_assign, 'w') as f:
        f.write("Inst | Length | Written in | Metadatum\n")
        f.write("----:|-------:|-----------:|-------------------------------------\n")
        for md in flat:
            f.write("0x{instruction:>02X} | {length:>6} | {gress:>10} | {name}\n".format(**md))

if args.p4:
    with open(args.p4, 'w') as f:
        f.write("// Metadata Instructions\n")
        f.write("enum bit<8> idint_mdid_t {\n")
        for i, md in enumerate(flat):
            f.write("    {p4:<16} = 0x{instruction:>02X}".format(**md))
            f.write(",\n" if i < (len(flat) - 1) else "\n")
        f.write("}\n")
