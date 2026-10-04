#!/usr/bin/env python3

import bibtexparser

lib = bibtexparser.parse_file("../final.bib")

icmc = []
other = []

for entry in lib.entries:
    if "booktitle" in entry.fields_dict != None and "computer music journal" in entry.fields_dict["booktitle"].value.lower():
        icmc.append(entry)
    else:
        other.append(entry)

bibtexparser.write_file("cmj.bib", bibtexparser.Library(icmc))
bibtexparser.write_file("not-cmj.bib", bibtexparser.Library(other))
