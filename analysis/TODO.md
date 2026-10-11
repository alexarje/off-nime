# TODO

## Now

- [ARJ] Export the NIME 2022 paper collections from PubPub (the export failed on 2026-10-10), then
  run `tools/pubpub_package.py 2022` and `tools/grobid_refs.py`.
- [ARJ] Decide on the Zenodo deposit of the 2021 proceedings (zips and CHECK.md in the archive's
  `2021/zenodo/`); 7 bibliography papers are missing from the export, probably in a collection
  that was not exported. [Recommendation: one record per year, the PubPub DOIs as related
  identifiers, with the steering committee's agreement.]

- [ARJ] ARL after the threshold change: the agents rated close calls you may want to check, such as
  premieres with no venue named, university ensembles (Stanford Laptop Orchestra, L2Ork), works
  credited with festivals only in a performer's biography (held at 6), and a few weak 7s (a
  university-run festival, works published on the internet, the Danish music museum). The reasons
  are in `output/trl_arl.tsv`.
- [ARJ] TRL after the alignment at 6/7: close calls are title-only NIME 2010 and 2016 concert
  entries (now TRL 6, was mostly 5), pieces called a "study" (held at 5), teaching papers kept at 7
  on courses taught repeatedly, and short abstracts of devices probably used widely but not stated
  so (LEMUR, Augmented Violin, Samchillian, lowered). The TRL reasons are in the `trl_reason`
  column of `output/trl_arl.tsv`.
- [ARJ] Six studies on estimating and adapting the TRL are now cited in the paper; the other
  candidates, with notes, are in the paper folder (`trl_literature.md`, `trl_literature.bib`).
- [ARJ] Label `output/trl_validation_sheet.tsv` (30 entries, your TRL and ARL) so agreement can be measured.
- [ARJ] Vet `bibs/Historical/historical.bib`: 13 works not found in a catalogue carry a note
  (among them the Sax patent and the Hornbostel–Sachs article); add or remove seeds in
  `tools/historical_seeds.txt`.
- [ARJ] Vet `bibs/Zotero/zotero.bib` (works from your library, title classifier only); the
  library also holds works on other fields, and a few may have slipped through.
- [ARJ] Ask the NIME steering committee to deposit the 2021 and 2022 proceedings on Zenodo
  (recommended), so that their texts can be read like the other years.
- [ARJ] Read Cited and Background and move what is on the wrong side (title classifier, 88% accurate).
- [ARJ] NIME bibliography: review `output/nime_missing_abstracts.tsv`; check the 2005 "NIME papers" that look
  like artworks and the front-matter entries among the 2019 music entries.

- [ARJ] Vet `bibs/Cited/cited.bib` (admitted by rule) and remove what does not belong.
- [ARJ] Read the top of `output/borderline.tsv`: relevant reviews with short titles miss the
  closeness bar there.
- [ARJ] Check `output/offnime_dois_review.tsv` (near-miss DOI matches for off-NIME entries).
- [ARJ] Ask the ICMA or Michigan Publishing for a metadata export of the ICMC proceedings
  (recommended); the online archive and DBLP both block scripts with bot checks.
- [ARJ] Get a Semantic Scholar API key to finish the remaining off-NIME title lookups.
- Pull request to IDMIL/off-nime: on hold at Alexander's request.
- [ARJ] IDMIL/off-nime#7 (the Rosenboom1975 key), #8 (four duplicate entries and an author name) and
  #9 (abbreviated page ranges) await review; this fork already has the same changes.

## Next

- [ARJ] Skim `output/candidates_snowball2.tsv` (5 works from the second snowball round).
- [ARJ] Related, from the agent's TRL reading: `related:feldbusch2003thebtrcbluet` (a Bluetooth
  remote control) looks off topic, and `related:wall2010experimentin`, the virtual-reality game
  audio papers and the wave field synthesis overview are on the edge. `related:lab2003investigatio`
  has author and affiliation text in its title, from Crossref. [Recommendation: leave the rule as
  it is and drop single entries by hand once vetted, as for Theses.]
- [ARJ] Skim `bibs/Theses/theses.bib` (selected by rule) and `output/candidates_theses.tsv`;
  the theses admitted because they cite the archives include some general HCI and VR work.
- [ARJ] The theses admitted on an English title alone (their abstracts are in other languages)
  carry a note saying so; skim those in particular.

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

