# TODO

## Now

- [ARJ] Export the NIME 2022 paper collections from PubPub (the export failed on 2026-10-10), then
  run `tools/pubpub_package.py 2022` and `tools/grobid_refs.py`.
- [ARJ] Decide on the Zenodo deposit of the 2021 proceedings (zips and CHECK.md in the archive's
  `2021/zenodo/`); 7 bibliography papers are missing from the export, probably in a collection
  that was not exported. [Recommendation: one record per year, the PubPub DOIs as related
  identifiers, with the steering committee's agreement.]

- [ARJ] The vetting recommendations are applied (`tools/hand.tsv`: 131 removals, 54 moves between
  Cited and Background, 57 corrections). The 207 close calls stay in; they are listed with reasons
  in `data/vetting_sheet.tsv` (private) if you want to drop any.
- [ARJ] ARL after the threshold change: the agents rated close calls you may want to check, such as
  premieres with no venue named, university ensembles (Stanford Laptop Orchestra, L2Ork), works
  credited with festivals only in a performer's biography (held at 6), and a few weak 7s (a
  university-run festival, works published on the internet, the Danish music museum). The reasons
  are in `output/trl_arl.tsv`.
- [ARJ] TRL, estimated blind to the ARL for every NIME paper and concert or installation with an
  ARL: close calls are title-only concert entries (TRL 6 by default), software called freely
  available (8, or 7 without a stated release), commercial hardware inside a new setup (the setup
  is rated, not the hardware), and survey or interview papers about established technology (9 or
  null). The TRL reasons are in the `trl_reason` column of `output/trl_arl.tsv`.
- [ARJ] Six studies on estimating and adapting the TRL are now cited in the paper; the other
  candidates, with notes, are in the paper folder (`trl_literature.md`, `trl_literature.bib`).
- [ARJ] Label `output/trl_validation_sheet.tsv` (30 entries, your TRL and ARL) so agreement can be measured.
- [ARJ] Ask the NIME steering committee to deposit the 2021 and 2022 proceedings on Zenodo
  (recommended), so that their texts can be read like the other years.
- [ARJ] NIME bibliography: review `output/nime_missing_abstracts.tsv`; check the 2005 "NIME papers" that look
  like artworks and the front-matter entries among the 2019 music entries.

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

- [ME] `nime2020_117` is font-shifted and its PDF returns 404 at nime.org; find it elsewhere and OCR it
  with `tools/ocr_texts.py`.
- [ARJ] Skim `output/candidates_snowball2.tsv` (5 works from the second snowball round).

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

