# TODO

## Now

- [ARJ] Export the NIME 2022 paper collections from PubPub (the export failed on 2026-10-10), then
  run `tools/pubpub_package.py 2022` and `tools/grobid_refs.py`.
- [ARJ] Decide on the Zenodo deposit of the 2021 proceedings (zips and CHECK.md in the archive's
  `2021/zenodo/`); 7 bibliography papers are missing from the export, probably in a collection
  that was not exported. [Recommendation: one record per year, the PubPub DOIs as related
  identifiers, with the steering committee's agreement.]

- [ARJ] Label `output/trl_validation_sheet.tsv` (30 entries, your TRL and ARL) so agreement can be measured.
- [ARJ] Vet `bibs/Historical/historical.bib`: 13 works not found in a catalogue carry a note
  (among them the Sax patent and the Hornbostel–Sachs article); add or remove seeds in
  `tools/historical_seeds.txt`.
- [ARJ] Vet `bibs/Zotero/zotero.bib` (528 works from your library, title classifier only); the
  library also holds works on other fields, and a few may have slipped through.
- [ARJ] Ask the NIME steering committee to deposit the 2021 and 2022 proceedings on Zenodo
  (recommended), so that their texts can be read like the other years.
- [ARJ] Read Cited and Background and move what is on the wrong side (title classifier, 88% accurate).
- [ARJ] NIME bibliography: review `output/nime_missing_abstracts.tsv`; check the 2005 "NIME papers" that look
  like artworks and the front-matter entries among the 2019 music entries.

- [ARJ] Vet `bibs/Cited/cited.bib` (170 works admitted by rule) and remove what does not belong.
- [ARJ] Read the top of `output/borderline.tsv`: relevant reviews with short titles miss the
  closeness bar there.
- [ARJ] Check `output/offnime_dois_review.tsv` (near-miss DOI matches for off-NIME entries).
- [ARJ] Ask the ICMA or Michigan Publishing for a metadata export of the ICMC proceedings
  (recommended); the online archive and DBLP both block scripts with bot checks.
- [ARJ] Pushes to the fork do not trigger the Pages workflow; enabling workflows in the fork's
  Actions tab may fix it. Until then, deploy with `gh workflow run` (see HANDOVER.md).
- [ARJ] Get a Semantic Scholar API key to finish the remaining off-NIME title lookups.
- Pull request to IDMIL/off-nime: on hold at Alexander's request.

## Next

- [ARJ] Skim `output/candidates_snowball2.tsv` (5 works from the second snowball round).
- [ME] Fix aggregator school names (Zenodo, NORA, ERA, LA Referencia) in the thesis records.
- [ARJ] Skim `bibs/Theses/theses.bib` (409, selected by rule) and `output/candidates_theses.tsv`;
  the theses admitted because they cite the archives include some general HCI and VR work.
- [ME] 1,866 non-English theses are listed in `output/candidates_theses_non_english.tsv`, most of
  them French from theses.fr.
- [ME] One TRL estimate is duplicated in the batches (off-nime:Chadabe1975); harmless, the
  merge keeps the last.

## Later

- [ARJ/ME] Theses from the community (#5), once the site is public under IDMIL:
  1. [ME] A GitHub issue form, "Suggest a thesis" (title, author, year, institution, link, and
     whether it is the sender's own), in the repository that hosts the site, so suggestions are
     public and nothing personal is stored elsewhere. [Recommendation: in IDMIL/off-nime after the
     pull request, since a call pointing at a fork would move later.]
  2. [ME] A link to the form from the Theses tab, with the admission rule in one sentence.
  3. [ARJ] A short call on the NIME mailing list and at the NIME business meeting: "Is your thesis
     here?", with the link to the Theses tab and the form.
  4. [ME] A script that reads the issues, looks each thesis up (DataCite, OpenAlex, theses.fr) and
     adds it to a hand-vetted list that theses.py admits without a score, with the issue number in
     the note.

