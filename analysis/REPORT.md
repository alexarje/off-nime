---
title: "How complete are the NIME and off-NIME archives? A citation, author and topic analysis"
author: Alexander Refsum Jensenius
date: 2026-10-09
layout: page
data: NIME-bibliography (paper, music, installation and alt proceedings) and off-NIME (CMJ, ICMC, ISIDM, Extras)
---

## Abstract

The NIME proceedings and the off-NIME archive together hold 3936 entries: 3020 from the NIME conference (2001–2026) and 916 from earlier and concurrent publications (1955–2013). This report asks how complete the two archives are as a record of the field, measured by what their papers cite and what cites them. From 32167 references parsed out of 2199 paper texts, and from Semantic Scholar's forward citations, there are 9571 citation links between archive entries. 355 works are cited by at least five archive papers but held by neither archive, and 1209 works outside NIME cite at least five archive entries. Two further lists rank papers as NIME-related but missing: 338 in a local archive of conference proceedings, and 436 in 7 journals and two proceedings series swept through Crossref. Together they are a curation queue for extending off-NIME backwards, sideways and past its current end in 2013. An [interactive atlas](../atlas/) of the papers, authors and citations accompanies the report.

## Data

The NIME side is the `NIME-bibliography` repository: 2448 papers, 488 music entries, 70 installation entries and 14 alt entries. Papers carry abstracts, and many carry keywords. The off-NIME side is this repository: 94 Computer Music Journal entries, 255 ICMC entries, 531 ISIDM entries and 36 extras. Off-NIME entries carry titles but no abstracts. Classified by where they were published, the off-NIME entries fall into these channels:

| Channel | Entries |
|---|---|
| ICMC | 253 |
| Other conference proceedings | 122 |
| Computer Music Journal | 106 |
| Books | 102 |
| Other journals | 86 |
| Book chapters | 36 |
| Organised Sound | 33 |
| Theses | 32 |
| IRCAM publications | 23 |
| CHI / HCI | 21 |
| Leonardo | 19 |
| AES | 17 |
| Contemporary Music Review | 17 |
| Technical reports | 14 |
| Journal of New Music Research | 12 |
| Sound and Music Computing | 7 |
| SIGGRAPH / graphics | 7 |
| Acoustical Society | 4 |
| Gesture workshops | 3 |
| DAFx | 2 |

Paper texts came from three places. 2285 NIME paper PDFs were downloaded from nime.org and reduced to text, keeping no PDF. 24 early NIME papers whose PDFs have broken font encodings were read from OCR copies in a local archive of conference proceedings. 21 curated off-NIME ICMC papers were matched to local ICMC PDFs by year, first author and title. Semantic Scholar was queried by DOI and found 1966 of the 2448 NIME papers (80.3%) and 260 off-NIME entries.

## Method

Authors are keyed on surname and first initial, with accents removed, so that "Marcelo M. Wanderley" and "M. Wanderley" are one node; the cost is that a few different people share a key. Topics come from a non-negative matrix factorisation (16 components) of TF-IDF vectors over title, keywords and abstract, fitted on papers only and then applied to the concert and installation notes. The paper map is a t-SNE projection of the same vectors. The co-author and citation networks are laid out with ForceAtlas2; the co-author network's small components are packed in a band below its main component.

References were split from each text's last References heading on numbered markers, or on author–year line starts where there are none, and matched to the archives on a title key (significant words run together, 32 letters) or on the archive title appearing in the reference string. Unmatched references were clustered on the same key. 4347 references (13.5%) yielded no usable title.

Two checks bound the parser's quality. A parsed link from a paper to one published more than a year later must be wrong; of 6043 parsed links, 0 do so. Recall was measured against the 385 links that Semantic Scholar's own reference lists give for papers the parser also read: the parser finds 53.0% of them. Most misses come from pdftotext interleaving the two columns of a page, which breaks a reference in half. The citation network therefore merges the parsed links with Semantic Scholar's links in both directions.

Semantic Scholar holds the NIME papers but returns their reference lists elided at the publisher's request; only 141 entries came with references. Forward citations are not elided, and they give the second candidate list.

The local conference archive was scored separately. Each of its 1339 paper texts (ICMC, DAFx, SMC, ISMIR, ICMPC and workshops; duplicates, programme books and whole volumes removed) is represented by its first page and scored by its mean cosine similarity to its ten nearest archive entries, leaving out a paper's own archive entry where it has one. As a check that the score can fail, the 44 curated off-NIME ICMC papers present locally were scored in the same way. They rank at a median percentile of 73.6 among 685 ICMC texts, and 50.0% of them fall in the top quarter, against 50 and 25 by chance. A candidate is listed as above threshold when it scores at least as high as the lowest quarter of the curated papers.

A Crossref sweep covered every article in ACM Transactions on Computer-Human Interaction, Computer Music Journal, Contemporary Music Review, Journal of New Music Research, Leonardo Music Journal, Organised Sound and Personal and Ubiquitous Computing, and music-related papers in the CHI and TEI proceedings: 8268 research articles of at least four title words, 2328 of them with an abstract. Short titles such as record and product reviews score high on closeness alone, since they share common words with everything, so these articles are scored by contrast: closeness to the archives minus closeness to the rest of the sweep. Here the check is the 101 Computer Music Journal articles already curated into off-NIME. They rank at a median percentile of 75.4 among 1623 CMJ articles, and 50.5% fall in the top quarter. A candidate needs at least the curated median contrast and at least the curated lower-quartile closeness, so that general HCI articles far from the music-heavy sweep do not pass on contrast alone.

The works on the backward list were looked up in Crossref by title, first author and year, accepting a hit whose title matches at a ratio of at least 0.9 and whose year is within two. 190 of 355 (53.5%) were found; the rest have no Crossref record, as with arXiv preprints and older conference papers, or titles parsed too poorly to match.

## Results

### Two archives, few shared authors

The archives have 4457 authors between them: 1034 in off-NIME and 3720 in NIME. Only 297 (6.7%) appear in both. 3064 authors (68.7%) have a single entry. The co-author network has 8262 links, and its largest connected component holds 2567 authors (57.6%); the atlas shows the 1393 authors with at least two entries. The authors who bridge the two archives are, unsurprisingly, the founding generation of the conference:

| Author | Off-NIME | NIME | First entry |
|---|---|---|---|
| Marcelo M. Wanderley | 26 | 80 | 1996 |
| Joseph A. Paradiso | 18 | 28 | 1996 |
| Perry R. Cook | 14 | 13 | 1989 |
| David Wessel | 9 | 8 | 1979 |
| Haruhiro Katayose | 11 | 7 | 1993 |
| Sidney S. Fels | 7 | 17 | 1994 |
| Roger B. Dannenberg | 6 | 14 | 1984 |
| Julius O. Smith | 6 | 12 | 1992 |
| Adrian Freed | 6 | 18 | 1991 |
| Atau Tanaka | 5 | 21 | 1991 |
| Matthew Wright | 5 | 29 | 1994 |
| Antonio Camurri | 11 | 5 | 1986 |

### Topics

| # | Strongest terms | Off-NIME | NIME |
|---|---|---|---|
| 1 | installation, collaborative, process, composition, experience, space | 111 | 618 |
| 2 | motion, computers dance, environments, analysis dance, platform, club | 87 | 66 |
| 3 | gestures, gesture recognition, space, gesture analysis, sensor, expressive gesture | 43 | 90 |
| 4 | virtual reality, virtual environments, presence, immersive, physical, virtual environment | 44 | 118 |
| 5 | midi controller, controllers, foot controller, programmable, gestural controller, alternative | 31 | 118 |
| 6 | parameters, synthesizer, sounds, models, granular synthesis, voice | 40 | 201 |
| 7 | feedback, sensors, haptic, physical, sensor, force | 97 | 376 |
| 8 | input devices, evaluation input, expression, input device, mobile, space | 46 | 95 |
| 9 | keyboard, synthesizer, modular, touch, piano, polyphonic | 43 | 65 |
| 10 | media, installation, language, understanding, philosophy, reader | 34 | 71 |
| 11 | live electronics, live coding, graphical, aesthetics, composition, audio-visual | 42 | 201 |
| 12 | mapping strategies, mappings, controllers, parameters, motion, expressive | 37 | 129 |
| 13 | gestural synthesis, gestural controller, instrumental, gestures, gestural input, environments | 52 | 158 |
| 14 | human-computer interaction, tangible, human, musicians, perception, hci | 47 | 242 |
| 15 | machine learning, neural, model, models, gestures, algorithms | 66 | 301 |
| 16 | programming, improvisation, max msp, processing, virtual environment, integrated environment | 41 | 134 |

Shares are mean topic weights per five-year period. In the off-NIME archive, the earliest period (1975–1979) is dominated by keyboard, synthesizer (24.8%) and parameters, synthesizer (18.6%). In NIME, from 2000–2004 to 2025–2029, the largest rises are in installation, collaborative (13.4% to 25.8%) and machine learning, neural (5.1% to 12.6%), and the largest falls in midi controller, controllers (13.2% to 2.1%) and input devices, evaluation input (6.6% to 2.6%). The trends tab in the atlas shows every topic and period. I would treat the topic model as a map for browsing rather than a finding, since off-NIME entries have titles only.

### Citations between the archives

Of the 9571 citation links, 6714 go from NIME to NIME and 2322 from NIME to off-NIME, so 25.7% of NIME's links into the archives point to off-NIME. In the other direction, 200 links go from off-NIME entries to NIME papers and 335 within off-NIME. The off-NIME figures are low because few off-NIME texts were available to parse, not because those papers cite little. The most cited entries within the archives are:

| Title | Year | Channel | Cited by |
|---|---|---|---|
| Problems and Prospects for Intimate Musical Control of Computers | 2002 | Computer Music Journal | 139 |
| Principles for Designing Computer Music Controllers | 2001 | NIME | 119 |
| The importance of Parameter Mapping in Electronic Instrument Design | 2002 | NIME | 99 |
| Input Devices for Musical Expression : Borrowing Tools from HCI | 2001 | NIME | 89 |
| Trends in Gestural Control of Music | 2000 | Books | 75 |
| New digital musical instruments: control and interaction beyond the keyboard | 2006 | Books | 65 |
| The E in NIME: Musical Expression with New Computer Interfaces | 2006 | NIME | 57 |
| Mapping performer parameters to synthesis engines | 2002 | Organised Sound | 55 |
| Evaluation of Input Devices for Musical Expression: Borrowing Tools from HCI | 2002 | Computer Music Journal | 51 |
| Contexts of Collaborative Musical Experiences | 2003 | NIME | 49 |
| Designing Constraints: Composing and Performing with Digital Musical Systems | 2010 | Computer Music Journal | 45 |
| Of Epistemic Tools: Musical Instruments as Cognitive Extensions | 2009 | Organised Sound | 44 |
| Mapping Transparency through Metaphor: towards more expressive musical instruments | 2002 | Organised Sound | 43 |
| Gestural Control of Sound Synthesis | 2004 | Other conference proceedings | 40 |
| A Framework for the Evaluation of Digital Musical Instruments | 2011 | Computer Music Journal | 39 |

### What is missing: three lists

The first list holds works that archive papers cite but neither archive holds, in [`candidates_cited.bib`](output/candidates_cited.bib) (355 works cited at least five times, 190 with a DOI). These are the foundations the archives leave out: protocols and languages, books on embodiment and gesture, HCI theory, and later NIME-adjacent journal articles.

| Cited by | First author | Year | Title |
|---|---|---|---|
| 48 | wright | 1997 | Open SoundControl: A New Protocol for Communicating with Sound Synthesizers |
| 40 | jorda | 2007 | The reacTable: exploring the synergy between live music performance and on Tangible and embedded interaction |
| 35 | caillon | 2021 | RAVE: A variational autoencoder for fast and high-quality neural audio synthesis |
| 33 | braun | 2006 | Using thematic analysis in psychology |
| 30 | leman | 2007 | Embodied Music Cognition and Mediation Technology |
| 29 | magnusson | 2019 | Sonic Writing: Technologies of Material, Symbolic, and Signal Inscriptions |
| 28 | morreale | 2023 | NIME Principles & Code of Practice on Ethical Research |
| 28 | mcpherson | 2015 | An Environment for Submillisecond-Latency Audio and Sensor Processing on BeagleBone Black |
| 27 | frid | 2019 | Accessible digital musical instruments—a review of musical interfaces in inclusive music practice |
| 25 | dourish | 2001 | Where the action is: the foundations of embodied interaction |
| 25 | barbosa | 2003 | Displaced soundscapes: A survey of network systems for music and sonic art creation |
| 24 | godøy | 2010 | Musical Gestures: Sound, Movement, and Meaning |
| 24 | mcpherson | 2010 | The magnetic resonator piano: Electronic augmentation of an acoustic grand piano |
| 24 | mccartney | 2002 | Rethinking the computer music language: Supercollider |
| 22 | jorda | 2005 | Digital Lutherie: Crafting musical computers for new musics’ performance and improvisation |
| 21 | fiebrink | 2010 | The Wekinator: a system for real-time, interactive machine learning in music |
| 21 | kapur | 2005 | A history of robotic musical instruments |
| 21 | wright | 2005 | Open sound control: an enabling technology for musical networking |
| 20 | collins | 2003 | Live coding in laptop performance |
| 19 | small | 1998 | Musicking: The Meanings of Performing and Listening |
| 19 | cascone | 2000 | The Aesthetics of Failure: “Post-Digital” Tendencies in Contemporary Computer Music |
| 19 | frauenberger | 2019 | Entanglement HCI The Next Wave? |
| 19 | pachet | 2003 | The continuator: Musical interaction with style |
| 18 | o’modhrain | 2000 | Playing by Feel: Incorporating Haptic Feedback into Computer-Based Musical Instruments |
| 18 | trueman | 2007 | Why a laptop orchestra? |
| 17 | serafin | 2016 | Virtual reality musical instruments: State of the art, design principles, and future directions |
| 17 | barad | 2007 | Meeting the universe halfway: Quantum physics and the entanglement of matter and meaning |
| 17 | scipio | 2003 | ‘Sound is the interface’: From interactive to ecosystemic signal processing |
| 16 | ishii | 1997 | Tangible bits: towards seamless interfaces between people, bits and atoms |
| 16 | jensenius | 2022 | Sound Actions: Conceptualizing Musical Instruments |

The second list holds works outside NIME that cite at least five archive entries, in [`candidates_citing.tsv`](output/candidates_citing.tsv) (1209 works, 572 of them without a venue in Semantic Scholar, which mostly means theses). These are the continuation of the field outside its own proceedings: PhD theses, journal reviews, books and courses.

| Cites | Year | Title | Venue |
|---|---|---|---|
| 76 | 2026 | A Design Space for Live Music Agents | International Conference on Human Factors in Computing Systems |
| 59 | 2019 | New Directions in Music and Human-Computer Interaction | Springer Series on Cultural Computing |
| 58 | 2016 | Body as instrument : an exploration of gestural interface design |  |
| 57 | 2012 | Interactive music: Balancing creative freedom with musical development. |  |
| 53 | 2015 | Computed fingertip touch for the instrumental control of musical sound with an excursion on the computed retinal afterimage | arXiv.org |
| 48 | 2019 | Musical Instruments for Novices: Comparing NIME, HCI and Crowdfunding Approaches | New Directions in Music and Human-Computer Interaction |
| 46 | 2017 | Mobile Devices as Musical Instruments - State of the Art and Future Prospects | Computer Music Modeling and Retrieval |
| 46 |  | A Scale-Based Ontology of Digital Musical Instrument Design |  |
| 45 | 2016 | Creativity, exploration and control in musical parameter spaces |  |
| 42 | 2013 | Methods and Technologies for Analysing Links Between Musical Sound and Body Motion |  |
| 40 | 2011 | Advances in new interfaces for musical expression | International Conference on Computer Graphics and Interactive Techniques |
| 40 | 2009 | Creating new interfaces for musical expression: introduction to NIME | SIGGRAPH Courses |
| 39 | 2015 | How to design and build new musical interfaces | IFIP TC13 International Conference on Human-Computer Interaction |
| 39 | 2014 | How to design and build musical interfaces | SIGGRAPH ASIA Courses |
| 39 | 2013 | Creating new interfaces for musical expression | SIGGRAPH ASIA Courses |
| 38 | 2017 | Modeling, recognition of finger gestures and upper-body movements for musical interaction design |  |
| 38 | 2019 | Designing Digital Musical Instruments Using Probatio | Computational Synthesis and Creative Systems |
| 38 | 2017 | Score instruments : a new paradigm of musical instruments to guide musical wonderers |  |
| 37 | 2005 | Digital lutherie - crafting musical computers for new musics' performance and improvisation |  |
| 36 | 2016 | Apps, Agents, and Improvisation: Ensemble Interaction with Touch-Screen Digital Musical Instruments |  |

The third list holds papers in the local conference archive that score as NIME-related but are in neither archive, in [`candidates_local.tsv`](output/candidates_local.tsv) (338 above threshold, 229 of them from ICMC). Titles are guessed from the first page and need checking.

| Score | Set | Year | Title (guessed from the first page) |
|---|---|---|---|
| 0.301 | ICMC | 2008 | DEVELOPMENT OF A REAL-TIME GESTURAL INTERFACE FOR HANDS-FREE MUSICAL PERFORMANCE CONTROL |
| 0.268 | ICMC | 2008 | DEVELOPMENT OF A REAL−TIME GESTURAL INTERFACE FOR HANDS−FREE MUSICAL PERFORMANCE CONTROL |
| 0.262 | ICMC | 2005 | TOWARDS AN AUTOMATED MUSIC TEACHING SYSTEM: AUTOMATIC RECOGNITION OF MUSICAL |
| 0.261 | ICMC | 2008 | DO MOBILE PHONES DREAM OF ELECTRIC ORCHESTRAS? Henri Penttinen |
| 0.244 | ICMC | 2005 | DESIGNING AND IMPLEMENTING THE CHUCK PROGRAMMING LANGUAGE Perry R. Cook† Ananya Misra |
| 0.229 | ICMC | 2000 | An Expressive Synthesis Model for Bowed String Instruments Tapio Takala 1, Jarmo Hiipakka 1,3, Mikael Laurson  |
| 0.226 | ICMC | 2008 | Research Staff Michael Alcorn Michael Alcorn’s compositional interests lie at the intersection |
| 0.226 | ICMC | 2008 | SCORING THE COLOR OF WAITING Margaret Schedel |
| 0.226 | ICMC | 2001 | Data driven identification and computer animation of bowed string model |
| 0.223 | DAFx | 2006 |  |
| 0.219 | ICMC | 2000 | Influence of Attack Parameters on the Playability of a Virtual Bowed String Instrument |
| 0.216 | GestureWorkshop | 2003 | A Video System for Recognizing Gestures by Artificial Neural Networks for Expressive Musical Control |
| 0.213 | ICMC | 2001 | An Audio-Driven Perceptually Meaningful Timbre Synthesizer Tristan Jehan, Bernd Schoner∗ |
| 0.212 | ICMC | 2001 | Real Time Extended Physical Models for the Composer and Performer |
| 0.210 | ICMC | 2000 | Qualitative and Quantitive Assessment of a Virtual Bowed String Instrument |

The fourth list holds journal and proceedings papers that score as NIME-related, in [`candidates_journals.bib`](output/candidates_journals.bib) (436 papers: 113 from Computer Music Journal, 83 from Personal and Ubiquitous Computing, 71 from Contemporary Music Review, 69 from Journal of New Music Research, 54 from CHI, 24 from Leonardo Music Journal, 10 from Organised Sound, 10 from TEI, 2 from ACM Transactions on Computer-Human Interaction).

| Score | Source | Year | Title |
|---|---|---|---|
| 0.179 | Contemporary Music Review | 1991 | The UPIC as a performance instrument |
| 0.167 | Journal of New Music Research | 2002 | The Basics of Scratching |
| 0.140 | Computer Music Journal | 2001 | From Dance! to “Dance”: Distance and Digits |
| 0.138 | Computer Music Journal | 2020 | Electronic_Khipu_: Thinking in Experimental Sound from an Ancestral Andean Interface |
| 0.134 | Journal of New Music Research | 2018 | Symbaline: An electromagnetically actuated wine glass instrument |
| 0.121 | Contemporary Music Review | 2019 | Choreography in R. Murray Schafer's The Crown of Ariadne—Technical or Theatrical? |
| 0.120 | Computer Music Journal | 1986 | Elementi di Informatica Musicale |
| 0.107 | Journal of New Music Research | 2002 | The Exbow MetaSax: Compositional Applications of Bowed String Physical Models Using Instrument Controller Subsititution |
| 0.107 | Contemporary Music Review | 2010 | The Real-Time-Score: Nucleus and Fluid Opus |
| 0.103 | Computer Music Journal | 2017 | Real-Time Timbre Classification for Tabletop Hand Drumming |
| 0.100 | Journal of New Music Research | 2001 | Meter and Periodicity in Musical Performance |
| 0.096 | Computer Music Journal | 1977 | Unplayed by Human Hands |
| 0.087 | Computer Music Journal | 2015 | Designing Musical Instruments for the Browser |
| 0.087 | Computer Music Journal | 2015 | Expressive Robotic Guitars: Developments in Musical Robotics for Chordophones |
| 0.084 | Computer Music Journal | 1995 | 3-D Sound for Virtual Reality and Multimedia |
| 0.082 | Computer Music Journal | 1985 | TM +, Trio instrumental electroacoustique |
| 0.080 | Computer Music Journal | 2020 | Construction and Performance Applications of an Augmented Violin: TRAVIS II |
| 0.078 | Personal and Ubiquitous Computing | 1998 | Palmtop programmable appliance controls |
| 0.074 | Computer Music Journal | 2020 | Performer Experience on a Continuous Keyboard Instrument |
| 0.073 | Computer Music Journal | 1979 | A Microcomputer-Controlled Synthesis System for Live Performance |

### Data quality

The off-NIME archive holds 5 pairs of entries that share a title. Each pair is two publications: a conference paper and its journal version, reports in two issues of a journal, or two different papers with the same title.

| Entry | Same title as | Title |
|---|---|---|
| off-nime:czeiszperger92 | off-nime:tanaka90 | CyberArts International |
| off-nime:Buxton1978 | off-nime:buxton1978sssp | An Introduction to the SSSP Digital Synthesizer |
| off-nime:BosiLocalization1990 | off-nime:bosi90 | An Interactive Real-time System for the Control of Sound Localization |
| off-nime:wanderley2004gestural | off-nime:gibet1990gestural | Gestural Control of Sound Synthesis |
| off-nime:bromberg2004adapt | off-nime:bromberg2002adapt | ADaPT: Telepresent Artistic Collaborations |

3 titles occur in both archives. These are different publications of the same work, a NIME paper followed by a journal version, and both entries should stay.

| NIME entry | Off-NIME entry | Title |
|---|---|---|
| nime:nime2001_Wessel | off-nime:wessel2002intimate | Problems and Prospects for Intimate Musical Control of Computers |
| nime:nime2001_Ulyate | off-nime:ulyate2002interactive | The Interactive Dance Club : Avoiding Chaos In A Multi Participant Environment |
| nime:nime2008_KimBoyle | off-nime:kimboyle2009network | Network Musics --- Play , Engagement and the Democratization of Performance |

## Expanding the archives

I would extend off-NIME along the three directions the lists measure, and in this order.

1. Vet the Cited dataset and the borderline list. `bibs/Cited/cited.bib` holds 170 works admitted by fixed rules: each has a DOI, so its metadata comes from Crossref rather than from a parsed reference string; each is in neither archive; each is at least as close to the archives in wording as the lower quartile of the curated CMJ articles; and each is cited by at least 5 archive papers (81 works), cites at least 10 archive entries (109), or turned up in the journal sweep as well as on one of those lists (47). The website shows them under their own Cited tab. [`borderline.tsv`](output/borderline.tsv) lists 629 works with a DOI that fall short of one rule. Its top rows are clearly relevant reviews that miss the closeness bar only because their titles are short, so it needs a human reading. [ARJ: vet the top of the borderline list, and remove anything from Cited that does not belong.]
2. Use the forward list to continue off-NIME past 2013. Its top entries are mostly theses and journal articles that position themselves against NIME. The Crossref sweep gives a systematic list alongside the citation-driven one, and the two can be read together: an article that appears in both is a strong candidate.
3. Mine the local archive. ICMC 2000–2008 is present locally in full, and the score shortlists 229 ICMC papers. The full ICMC archive at the University of Michigan library, and ICMC's listing in DBLP, both sit behind bot checks, so they cannot be read by a script. [ARJ: ask the ICMA or Michigan Publishing for a metadata export of the ICMC proceedings (recommended), or extend the local copy year by year?]
4. Snowball. Each accepted candidate brings its own reference list; repeating the citation step until a round yields few new works cited by five or more archive papers would close the backward list.
5. Give every off-NIME entry a DOI or Semantic Scholar identifier, and an abstract where one exists. Topic modelling and citation matching both suffer most from titles-only entries. The Semantic Scholar title lookup is in `tools/fetch_s2.py` and resumes from its cache, but it needs an API key to finish in reasonable time. [ARJ: request a Semantic Scholar API key (recommended), or use OpenAlex's free daily allowance over several days?]
6. Decide where the result lives. The off-NIME site and the NIME bibliography share a format; a joined export with an `archive` field, as `data/corpus.json` already is, would let the NIME website show both. [ARJ: propose this to the IDMIL maintainers as a pull request (recommended), or keep it in this fork for now?]

### Exports

The joined collection, with the NIME proceedings, the off-NIME archive and the Cited dataset, is exported as [`collection.csv`](output/collection.csv) for spreadsheets and as CSL-JSON in [`collection.json`](output/collection.json), which Zotero, Mendeley and pandoc import directly. Each of its 4106 entries names its archive and dataset and, for archive entries, its strongest topic.

## Limitations

Author keys merge people who share a surname and initial, and split people who publish under different initials. The reference parser misses about half of the links that Semantic Scholar finds, so counts in the backward list are lower bounds and rank works by how often they are cited in papers whose text parsed well. The forward list depends on Semantic Scholar's coverage, which is better for recent work. Titles in the third list are guessed from first pages. The topic model is fitted on uneven text: abstracts for NIME, titles for off-NIME.

## Data and code

The scripts are in `analysis/tools/` and run from `analysis/.venv` in this order: `build_corpus.py`, `fetch_s2.py`, `fetch_citing.py`, `fetch_texts.py`, `extract_local.py`, `parse_refs.py`, `citations.py`, `crossref.py`, `local_candidates.py`, `score_journals.py`, `build_cited.py`, `offnime_dois.py`, `analyse.py`, `export.py`, `build_viewer.py` and `report.py`; `run.sh` runs them in that order. Downloaded texts and caches are in `analysis/data/` and are not committed. The atlas is `analysis/output/nime-atlas.html`; the candidate lists are the three `.tsv` files beside it.

## Contributor roles

Alexander Refsum Jensenius: conceptualisation, resources (the local conference archive), supervision. The NIME bibliography is maintained by the NIME community; the off-NIME archive was built at IDMIL, McGill University, under Marcelo M. Wanderley, by João Tragtenberg, Kasey Pocius, Maxwell Gentili-Morin and Ian Doherty.

## AI disclosure

The scripts, the analysis and the draft of this report were produced with Claude Opus 5.5 (Anthropic) in Claude Code, working from the instructions of the author. Paper metadata and citation links come from the Semantic Scholar Academic Graph API.
