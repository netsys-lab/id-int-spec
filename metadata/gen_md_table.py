#!/usr/bin/python3

import argparse
import yaml


parser = argparse.ArgumentParser(description="Format metadata definitions")
parser.add_argument("input", help="Metadata definitions")
parser.add_argument("--tables", default=None, help="Output file for tables ordered by category")
parser.add_argument("--inst-assign", default=None, help="Output file for instruction overview table")
parser.add_argument("--p4", default=None, help="Output file for P4 constants")
parser.add_argument("--go", default=None, help="Output file for Go constants")
parser.add_argument("--py", default=None, help="Output file for Python constants")
args = parser.parse_args()


with open(args.input, 'r') as file:
    defs = yaml.safe_load(file)

if args.tables:
    with open(args.tables, 'w') as f:
        f.write(f"# ID-INT Metadata Types\n")
        for i, group in enumerate(defs):
            if i > 0:
                f.write("\n")
            f.write(f"## {group['name']}\n\n")
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
                f.write("\n")
                for md in details:
                    f.write(f"### {md['name']}\n\n")
                    for line in md['details'].split("\n"):
                        f.write(f"{line}\n")

if args.inst_assign or args.p4 or args.go or args.py:
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
        f.write("// Metadata instructions\n")
        f.write("enum bit<8> idint_mdid_t {\n")
        for i, md in enumerate(flat):
            f.write("    {p4:<16} = 0x{instruction:>02X}".format(**md))
            f.write(",\n" if i < (len(flat) - 1) else "\n")
        f.write("}\n")

if args.go:
    with open(args.go, 'w') as f:
        f.write("// ID-INT instructions\n")
        f.write("const (\n")
        for i, md in enumerate(flat):
            f.write(f"    {'IdIntI' + md['p4'].title().replace('_', ''):<22} = 0x{md['instruction']:>02X}\n")
        f.write(")\n")

if args.py:
    with open(args.py, 'w') as f:
        f.write("# ID-INT instructions\n")
        f.write("_instructions = {\n")
        for i, md in enumerate(flat):
            f.write(f'    0x{md['instruction']:>02X}: "{md['p4'].lower()}",\n')
        f.write("}\n")
