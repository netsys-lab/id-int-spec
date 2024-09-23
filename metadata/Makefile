.PHONY: all
all: metadata.md instructions.md instructions.p4 instructions.go

metadata.md: metadata.yaml
	./gen_md_table.py metadata.yaml --tables metadata.md

instructions.md: metadata.yaml
	./gen_md_table.py metadata.yaml --inst-assign instructions.md

instructions.p4: metadata.yaml
	./gen_md_table.py metadata.yaml --go instructions.go

instructions.go: metadata.yaml
	./gen_md_table.py metadata.yaml --go instructions.go
