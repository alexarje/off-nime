---
title: "How complete are the NIME and off-NIME archives? A citation, author and topic analysis"
author: Alexander Refsum Jensenius
date: 2026-10-09
layout: page
data: NIME-bibliography (paper, music, installation and alt proceedings) and off-NIME (CMJ, ICMC, ISIDM, Extras)
---

## Abstract

The NIME proceedings and the off-NIME archive together hold {{records}} entries: {{n_nime}} from the NIME conference ({{nime_y0}}–{{nime_y1}}) and {{n_off}} from earlier and concurrent publications ({{off_y0}}–{{off_y1}}). This report asks how complete the two archives are as a record of the field, measured by what their papers cite and what cites them. From {{entries}} references parsed out of {{with_entries}} paper texts, and from Semantic Scholar's forward citations, there are {{edges}} citation links between archive entries. {{n_cited}} works are cited by at least five archive papers but held by neither archive, and {{n_citing}} works outside NIME cite at least five archive entries. Further lists rank papers as NIME-related but missing: {{loc_above}} in a local archive of conference proceedings, {{j_cands}} from a sweep of {{j_nsources}} journals and conference series, the music papers of six ACM proceedings and the Zenodo communities of open music-technology conferences, and {{sb_cands}} found by snowballing from the reference lists of the Cited works. Together they are a curation queue for extending off-NIME backwards, sideways and past its current end in {{off_y1}}. An [interactive atlas](../atlas/) of the papers, authors and citations accompanies the report.

## Data

The NIME side is the `NIME-bibliography` repository: {{n_nime_papers}} papers, {{n_music}} music entries, {{n_inst}} installation entries and {{n_alt}} alt entries. Papers carry abstracts, and many carry keywords. The off-NIME side is this repository: {{n_cmj}} Computer Music Journal entries, {{n_icmc}} ICMC entries, {{n_isidm}} ISIDM entries and {{n_extras}} extras. Off-NIME entries carry titles but no abstracts. Classified by where they were published, the off-NIME entries fall into these channels:

{{channels_table}}

Paper texts came from three places. {{src_web}} NIME paper PDFs were downloaded from nime.org and reduced to text, keeping no PDF. {{src_ocr}} early NIME papers whose PDFs have broken font encodings were read from OCR copies in a local archive of conference proceedings. {{src_icmc}} curated off-NIME ICMC papers were matched to local ICMC PDFs by year, first author and title. Semantic Scholar was queried by DOI and found {{s2_papers}} of the {{n_nime_papers}} NIME papers ({{s2_papers_pct}}) and {{s2_off}} off-NIME entries.

## Method

Authors are keyed on surname and first initial, with accents removed, so that "Marcelo M. Wanderley" and "M. Wanderley" are one node; the cost is that a few different people share a key. Topics come from a non-negative matrix factorisation ({{k_topics}} components) of TF-IDF vectors over title, keywords and abstract, fitted on papers only and then applied to the concert and installation notes. The paper map is a t-SNE projection of the same vectors. The co-author and citation networks are laid out with ForceAtlas2; the co-author network's small components are packed in a band below its main component.

References were split from each text's last References heading on numbered markers, or on author–year line starts where there are none, and matched to the archives on a title key (significant words run together, 32 letters) or on the archive title appearing in the reference string. Unmatched references were clustered on the same key. {{unkeyed}} references ({{unkeyed_pct}}) yielded no usable title.

Two checks bound the parser's quality. A parsed link from a paper to one published more than a year later must be wrong; of {{parsed_edges}} parsed links, {{later}} do so. Recall was measured against the {{recall_n}} links that Semantic Scholar's own reference lists give for papers the parser also read: the parser finds {{recall}}% of them. Most misses come from pdftotext interleaving the two columns of a page, which breaks a reference in half. The citation network therefore merges the parsed links with Semantic Scholar's links in both directions.

Semantic Scholar holds the NIME papers but returns their reference lists elided at the publisher's request; only {{s2_refs}} entries came with references. Forward citations are not elided, and they give the second candidate list.

The local conference archive was scored separately. Each of its {{loc_texts}} paper texts (ICMC, DAFx, SMC, ISMIR, ICMPC and workshops; duplicates, programme books and whole volumes removed) is represented by its first page and scored by its mean cosine similarity to its ten nearest archive entries, leaving out a paper's own archive entry where it has one. As a check that the score can fail, the {{loc_cur}} curated off-NIME ICMC papers present locally were scored in the same way. They rank at a median percentile of {{loc_med}} among {{loc_icmc}} ICMC texts, and {{loc_q}}% of them fall in the top quarter, against 50 and 25 by chance. A candidate is listed as above threshold when it scores at least as high as the lowest quarter of the curated papers.

A sweep through Crossref, Zenodo, HAL (for JIM) and SBC OpenLib (for SBCM) covered every article in {{j_sources}}, and music-related papers in the {{j_procs}} proceedings: {{j_items}} research articles of at least four title words, {{j_abs}} of them with an abstract. Short titles such as record and product reviews score high on closeness alone, since they share common words with everything, so these articles are scored by contrast: closeness to the archives minus closeness to the rest of the sweep. Here the check is the {{j_cur}} Computer Music Journal articles already curated into off-NIME. They rank at a median percentile of {{j_med}} among {{j_cmj}} CMJ articles, and {{j_q}}% fall in the top quarter. A candidate needs at least the curated median contrast and at least the curated lower-quartile closeness, so that general HCI articles far from the music-heavy sweep do not pass on contrast alone.

The works on the backward list were looked up in Crossref by title, first author and year, accepting a hit whose title matches at a ratio of at least 0.9 and whose year is within two. {{cr_ok}} of {{n_cited}} ({{cr_pct}}) were found; the rest have no Crossref record, as with arXiv preprints and older conference papers, or titles parsed too poorly to match.

## Results

### Two archives, few shared authors

The archives have {{authors}} authors between them: {{authors_off}} in off-NIME and {{authors_nime}} in NIME. Only {{authors_both}} ({{authors_both_pct}}) appear in both. {{single}} authors ({{single_pct}}) have a single entry. The co-author network has {{coedges}} links, and its largest connected component holds {{giant}} authors ({{giant_pct}}); the atlas shows the {{mapped}} authors with at least two entries. The authors who bridge the two archives are, unsurprisingly, the founding generation of the conference:

{{bridges_table}}

### Topics

{{topics_table}}

Shares are mean topic weights per five-year period. {{trend}} The trends tab in the atlas shows every topic and period. I would treat the topic model as a map for browsing rather than a finding, since off-NIME entries have titles only.

### Citations between the archives

Of the {{edges}} citation links, {{e_nn}} go from NIME to NIME and {{e_no}} from NIME to off-NIME, so {{e_no_pct}} of NIME's links into the archives point to off-NIME. In the other direction, {{e_on}} links go from off-NIME entries to NIME papers and {{e_oo}} within off-NIME. The off-NIME figures are low because few off-NIME texts were available to parse, not because those papers cite little. The most cited entries within the archives are:

{{most_cited_table}}

### What is missing: three lists

The first list holds works that archive papers cite but neither archive holds, in [`candidates_cited.bib`](output/candidates_cited.bib) ({{n_cited}} works cited at least five times, {{cr_ok}} with a DOI). These are the foundations the archives leave out: protocols and languages, books on embodiment and gesture, HCI theory, and later NIME-adjacent journal articles.

{{cited_table}}

The second list holds works outside NIME that cite at least five archive entries, in [`candidates_citing.tsv`](output/candidates_citing.tsv) ({{n_citing}} works, {{citing_untyped}} of them without a venue in Semantic Scholar, which mostly means theses). These are the continuation of the field outside its own proceedings: PhD theses, journal reviews, books and courses.

{{citing_table}}

The third list holds papers in the local conference archive that score as NIME-related but are in neither archive, in [`candidates_local.tsv`](output/candidates_local.tsv) ({{loc_above}} above threshold, {{loc_above_icmc}} of them from ICMC). Titles are guessed from the first page and need checking.

{{loc_table}}

The fourth list holds journal and proceedings papers that score as NIME-related, in [`candidates_journals.bib`](output/candidates_journals.bib) ({{j_cands}} papers: {{j_by_source}}).

{{j_table}}

The fifth list comes from one round of snowballing. {{sb_refs}} of the {{sb_cited}} Cited works have reference lists in Crossref, and [`candidates_snowball.tsv`](output/candidates_snowball.tsv) holds the {{sb_cands}} works that at least {{sb_min}} of them cite and that neither archive nor Cited holds. Proceedings and journal names are not counted as works, and a work cited both by DOI and by title is counted once.

{{sb_table}}

### Non-English proceedings

JIM and SBCM records are scored by their English title and abstract, which the repositories often give beside the original: {{ne_jim_en}} of {{ne_jim}} JIM papers and {{ne_sbcm_en}} of {{ne_sbcm}} SBCM papers have English text. The rest are listed unscored in [`candidates_nonenglish_unscored.tsv`](output/candidates_nonenglish_unscored.tsv). SBC OpenLib holds only the recent SBCM editions; the earlier proceedings, from 1994, are whole-volume PDFs that would need splitting into papers first.

### Theses

PhD and master's theses were collected separately, since they dominate the forward list and are poorly covered by the journals. {{th_q}} NIME-related queries to OpenAlex (works of type dissertation) and DataCite (Dissertation and Thesis records), and a DataCite title lookup of the untyped works on the forward list, gave {{th_n}} distinct theses, of which {{th_ne}} are not in English and are listed separately for the non-English sources ([`candidates_theses_non_english.tsv`](output/candidates_theses_non_english.tsv)).

Thresholds borrowed from the journal sweep admitted too few theses, since thesis abstracts read differently from article abstracts, so the thresholds are calibrated on the {{th_cal}} English theses known to cite the archives: closeness and contrast both at their median. Lower thresholds admitted many more theses, but a reading of sampled titles found many of them off topic (music education, performance practice, club culture, general computing), while recall on the check set below did not change. As a check on a separate population, the searches found {{th_known}} of the {{th_off}} theses already in off-NIME, and the rules would admit {{th_adm}} of them ({{th_pct}}%). [`bibs/Theses/theses.bib`](../bibs/Theses/theses.bib) holds the {{th_admitted}} admitted theses, {{th_cites}} of them because they cite at least three archive entries, and the website shows them under a Theses tab. The full scored list is [`candidates_theses.tsv`](output/candidates_theses.tsv).

### Data quality

The off-NIME archive holds {{n_dups}} pairs of entries that share a title. Each pair is two publications: a conference paper and its journal version, reports in two issues of a journal, or two different papers with the same title.

{{dups_table}}

{{n_cross}} titles occur in both archives. These are different publications of the same work, a NIME paper followed by a journal version, and both entries should stay.

{{cross_table}}

## Expanding the archives

I would extend off-NIME along the three directions the lists measure, and in this order.

1. Vet the Cited dataset and the borderline list. `bibs/Cited/cited.bib` holds {{c_adm}} works admitted by fixed rules: each has a DOI, so its metadata comes from Crossref rather than from a parsed reference string; each is in neither archive; each is at least as close to the archives in wording as the lower quartile of the curated CMJ articles; and each is cited by at least {{c_min_cited}} archive papers ({{c_by_cited}} works), cites at least {{c_min_citing}} archive entries ({{c_by_cites}}), or turned up in the journal sweep as well as on one of those lists ({{c_by_sweep}}). The website shows them under their own Cited tab. [`borderline.tsv`](output/borderline.tsv) lists {{c_border}} works with a DOI that fall short of one rule. Its top rows are clearly relevant reviews that miss the closeness bar only because their titles are short, so it needs a human reading. [ARJ: vet the top of the borderline list, and remove anything from Cited that does not belong.]
2. Use the forward list to continue off-NIME past {{off_y1}}. Its top entries are mostly theses and journal articles that position themselves against NIME. The Crossref sweep gives a systematic list alongside the citation-driven one, and the two can be read together: an article that appears in both is a strong candidate.
3. Mine the local archive. ICMC 2000–2008 is present locally in full, and the score shortlists {{loc_above_icmc}} ICMC papers. The full ICMC archive at the University of Michigan library, and ICMC's listing in DBLP, both sit behind bot checks, so they cannot be read by a script. [ARJ: ask the ICMA or Michigan Publishing for a metadata export of the ICMC proceedings (recommended), or extend the local copy year by year?]
4. Snowball. Each accepted candidate brings its own reference list; repeating the citation step until a round yields few new works cited by five or more archive papers would close the backward list.
5. Give every off-NIME entry a DOI or Semantic Scholar identifier, and an abstract where one exists. Topic modelling and citation matching both suffer most from titles-only entries. The Semantic Scholar title lookup is in `tools/fetch_s2.py` and resumes from its cache, but it needs an API key to finish in reasonable time. [ARJ: request a Semantic Scholar API key (recommended), or use OpenAlex's free daily allowance over several days?]
6. Decide where the result lives. The off-NIME site and the NIME bibliography share a format; a joined export with an `archive` field, as `data/corpus.json` already is, would let the NIME website show both. [ARJ: propose this to the IDMIL maintainers as a pull request (recommended), or keep it in this fork for now?]

### Exports

The joined collection, with the NIME proceedings, the off-NIME archive and the Cited dataset, is exported as [`collection.csv`](output/collection.csv) for spreadsheets and as CSL-JSON in [`collection.json`](output/collection.json), which Zotero, Mendeley and pandoc import directly. Each of its {{x_rows}} entries names its archive and dataset and, for archive entries, its strongest topic.

## Limitations

Author keys merge people who share a surname and initial, and split people who publish under different initials. The reference parser misses about half of the links that Semantic Scholar finds, so counts in the backward list are lower bounds and rank works by how often they are cited in papers whose text parsed well. The forward list depends on Semantic Scholar's coverage, which is better for recent work. Titles in the third list are guessed from first pages. The topic model is fitted on uneven text: abstracts for NIME, titles for off-NIME.

## Data and code

The scripts are in `analysis/tools/` and run from `analysis/.venv` in this order: `build_corpus.py`, `fetch_s2.py`, `fetch_citing.py`, `fetch_texts.py`, `extract_local.py`, `parse_refs.py`, `citations.py`, `crossref.py`, `local_candidates.py`, `score_journals.py`, `build_cited.py`, `offnime_dois.py`, `analyse.py`, `export.py`, `build_viewer.py` and `report.py`; `run.sh` runs them in that order. Downloaded texts and caches are in `analysis/data/` and are not committed. The atlas is `analysis/output/nime-atlas.html`; the candidate lists are the three `.tsv` files beside it.

## Contributor roles

Alexander Refsum Jensenius: conceptualisation, resources (the local conference archive), supervision. The NIME bibliography is maintained by the NIME community; the off-NIME archive was built at IDMIL, McGill University, under Marcelo M. Wanderley, by João Tragtenberg, Kasey Pocius, Maxwell Gentili-Morin and Ian Doherty.

## AI disclosure

The scripts, the analysis and the draft of this report were produced with Claude Opus 5.5 (Anthropic) in Claude Code, working from the instructions of the author. Paper metadata and citation links come from the Semantic Scholar Academic Graph API.
