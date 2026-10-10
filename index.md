---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: page
---

# Off-NIME: NIME papers, chapters and books published outside of the NIME Conference Proceedings

## What is this resource?

This website contains a table of <span id="blurb-count"></span> off-NIME references relevant to the NIME community: vetted datasets, Cited, Theses, Related and Background datasets selected by rule, and a Historical dataset of precursors. This includes materials from conferences that predated NIME (CMJ, ICMC; so-called ["prehistoric NIME"](https://nime.org/proceedings/2023/nime2023_8.pdf)) as well as concurrent conferences, publications, and books, from around 1955 to 2012 in the vetted datasets, to the present in the rule-selected datasets, and back to the seventeenth century in Historical. 

There are three primary datasets, represented by the radio buttons just above the table: CMJ, ICMC, and ISIDM ([the Interactive Systems and Instrument Design in Music Working Group](https://www.sensorwiki.org/isidm)). A fourth dataset, Cited, holds works about NIME topics that are cited by many NIME and off-NIME papers, or that cite many of them, selected by the rules in the [report](analysis/REPORT.html), a fifth, Theses, holds PhD and master's theses found in OpenAlex and DataCite, a sixth, Related, holds journal and conference papers from a sweep of music-technology venues, and a seventh, Background, holds works that many NIME papers cite but that are not themselves about NIME topics, such as philosophy, psychology and design theory. All four are selected by rule. An eighth, Historical, holds works on musical instruments and music technology published before 1957, the year of the first MUSIC program: treatises, articles and patents, either found in the archives' reference lists or chosen by hand, each checked against a library catalogue or patent record where one has it. If you would like to get involved with cleaning any references, or with adding new datasets/features, feel free to [submit a PR on the GitHub repo](https://github.com/IDMIL/off-nime/pulls). To suggest a missing work, [fill in the suggestion form](https://github.com/alexarje/off-nime/issues/new?template=suggest-entry.yml).

Other features of this table include the search bar, column sorting (click the header to sort), and the download all button below.

An [interactive atlas](atlas/) places these entries beside the NIME proceedings by topic, co-authorship and citation, and a [report](analysis/REPORT.html) lists the works that both archives are missing.

<head>
    <link rel="stylesheet" href="styles.css">
    <script src="scripts/num-entries.js" async></script>
    <script src="scripts/search-and-filter.js" async></script>
    <script src="scripts/sorttable.js" async></script>
    <script src="scripts/copy-bibtex.js" async></script>
    <script src="https://cdn.jsdelivr.net/npm/minisearch@7.2.0/dist/umd/index.min.js" async></script>
</head>

<button id="download-all-button" onclick="downloadAll()">Click here to download all entries as a single BibTeX file</button>

<input type="text" id="table-search" onkeyup="searchTable(); setNumEntries();" placeholder="Search...">

<div id="table-tabs">
    <p>Datasets:</p>
    <input type="radio" id="tab-all" name="table-tab" checked="checked" onclick="filterTable(''); setNumEntries();"><label for="tab-all">All</label>
    <input type="radio" id="tab-cmj" name="table-tab" onclick="filterTable('Computer Music Journal'); setNumEntries();"><label for="tab-cmj">CMJ</label>
    <input type="radio" id="tab-icmc" name="table-tab" onclick="filterTable('International Computer Music Conference'); setNumEntries();"><label for="tab-icmc">ICMC</label>
    <input type="radio" id="tab-isidm" name="table-tab" onclick="notFilterTable(['Computer Music Journal', 'International Computer Music Conference', '(Cited)', '(Theses)', '(Related)', '(Background)', '(Historical)']); setNumEntries();"><label for="tab-isidm">ISIDM + Extras</label>
    <input type="radio" id="tab-cited" name="table-tab" onclick="filterTable('(Cited)'); setNumEntries();"><label for="tab-cited">Cited</label>
    <input type="radio" id="tab-theses" name="table-tab" onclick="filterTable('(Theses)'); setNumEntries();"><label for="tab-theses">Theses</label>
    <input type="radio" id="tab-related" name="table-tab" onclick="filterTable('(Related)'); setNumEntries();"><label for="tab-related">Related</label>
    <input type="radio" id="tab-background" name="table-tab" onclick="filterTable('(Background)'); setNumEntries();"><label for="tab-background">Background</label>
    <input type="radio" id="tab-historical" name="table-tab" onclick="filterTable('(Historical)'); setNumEntries();"><label for="tab-historical">Historical</label>
</div>

<div class="scrollableTable">
<table id="bibliography-table" class="sortable">
    <thead>
        <th>Year</th>
        <th>Author(s)</th>
        <th>Title</th>
        <th>Type</th>
        <th>Publication</th>
        <th>Pages</th>
        <th>URL</th>
        <th>BibTeX</th>
    </thead>
    {% bibliography %}
</table>
</div>

<div id="num-entries"></div>
