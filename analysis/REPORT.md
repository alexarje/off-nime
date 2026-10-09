---
title: "How complete are the NIME and off-NIME archives? A citation, author and topic analysis"
author: Alexander Refsum Jensenius
date: 2026-10-09
layout: page
data: NIME-bibliography (paper, music, installation and alt proceedings) and off-NIME (CMJ, ICMC, ISIDM, Extras)
---

## Abstract

The NIME proceedings and the off-NIME archive together hold 3936 entries: 3020 from the NIME conference (2001–2026) and 916 from earlier and concurrent publications (1955–2013). This report asks how complete the two archives are as a record of the field, measured by what their papers cite and what cites them. From 32167 references parsed out of 2199 paper texts, and from Semantic Scholar's forward citations, there are 9571 citation links between archive entries. 355 works are cited by at least five archive papers but held by neither archive, and 1209 works outside NIME cite at least five archive entries. Further lists rank papers as NIME-related but missing: 338 in a local archive of conference proceedings, 583 from a sweep of 13 journals, two proceedings series and the Zenodo communities of open music-technology conferences, and 120 found by snowballing from the reference lists of the Cited works. Together they are a curation queue for extending off-NIME backwards, sideways and past its current end in 2013. An [interactive atlas](../atlas/) of the papers, authors and citations accompanies the report.

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

A sweep through Crossref and Zenodo covered every article in ACM Transactions on Computer-Human Interaction, Computer Music Journal, Computer Music Multidisciplinary Research, Contemporary Music Review, International Conference on Live Coding, Journal of New Music Research, Leonardo Music Journal, Nordic Sound and Music Computing, Organised Sound, Personal and Ubiquitous Computing, Sound and Music Computing, TENOR (music notation) and Web Audio Conference, and music-related papers in the CHI and TEI proceedings: 10778 research articles of at least four title words, 4811 of them with an abstract. Short titles such as record and product reviews score high on closeness alone, since they share common words with everything, so these articles are scored by contrast: closeness to the archives minus closeness to the rest of the sweep. Here the check is the 101 Computer Music Journal articles already curated into off-NIME. They rank at a median percentile of 75.0 among 1623 CMJ articles, and 50.5% fall in the top quarter. A candidate needs at least the curated median contrast and at least the curated lower-quartile closeness, so that general HCI articles far from the music-heavy sweep do not pass on contrast alone.

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
| 1 | collaborative, installation, composition, process, experience, audience | 107 | 554 |
| 2 | computers dance, environments, analysis dance, platform, dance movement, footwear | 89 | 66 |
| 3 | gestures, gesture recognition, space, gesture analysis, expressive gesture, instrumental gesture | 40 | 85 |
| 4 | virtual reality, virtual environments, immersive, presence, virtual environment, virtual space | 51 | 99 |
| 5 | midi controller, controllers, foot controller, gestural controller, programmable, alternative | 32 | 103 |
| 6 | synthesizer, sounds, gestural synthesis, granular synthesis, voice, synthesis parameters | 48 | 196 |
| 7 | sensors, sensor, wireless, motion, environment, software | 67 | 141 |
| 8 | input devices, evaluation input, input device, expression, mobile, analysis | 52 | 107 |
| 9 | keyboard, synthesizer, touch, modular, piano, polyphonic | 38 | 50 |
| 10 | media, installation, language, philosophy, reader, understanding | 31 | 67 |
| 11 | human-computer interaction, tangible, human, musicians, hci, readings | 35 | 132 |
| 12 | mapping strategies, mappings, instrumental, controllers, gestures, motion | 62 | 148 |
| 13 | live electronics, live coding, graphical, audio-visual, programming, aesthetics | 54 | 318 |
| 14 | physical, acoustic, guitar, string, playing, augmented | 82 | 451 |
| 15 | machine learning, models, model, algorithms, generative, training | 45 | 284 |
| 16 | haptic feedback, force feedback, vibrotactile feedback, tactile feedback, haptics, visual feedback | 33 | 182 |

Shares are mean topic weights per five-year period. In the off-NIME archive, the earliest period (1975–1979) is dominated by synthesizer, sounds (20.1%) and keyboard, synthesizer (19.8%). In NIME, from 2000–2004 to 2025–2029, the largest rises are in collaborative, installation (11.9% to 23.2%) and machine learning, models (4.4% to 11.4%), and the largest falls in midi controller, controllers (11.3% to 1.8%) and input devices, evaluation input (7.2% to 2.8%). The trends tab in the atlas shows every topic and period. I would treat the topic model as a map for browsing rather than a finding, since off-NIME entries have titles only.

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

The fourth list holds journal and proceedings papers that score as NIME-related, in [`candidates_journals.bib`](output/candidates_journals.bib) (583 papers: 137 from Sound and Music Computing, 111 from Computer Music Journal, 73 from Personal and Ubiquitous Computing, 72 from Contemporary Music Review, 66 from Journal of New Music Research, 49 from CHI, 22 from International Conference on Live Coding, 21 from Leonardo Music Journal, 10 from Organised Sound, 9 from TEI, 8 from Computer Music Multidisciplinary Research, 2 from ACM Transactions on Computer-Human Interaction, 2 from TENOR (music notation), 1 from Web Audio Conference).

| Score | Source | Year | Title |
|---|---|---|---|
| 0.168 | Contemporary Music Review | 1991 | The UPIC as a performance instrument |
| 0.167 | Journal of New Music Research | 2002 | The Basics of Scratching |
| 0.141 | Computer Music Journal | 2001 | From Dance! to “Dance”: Distance and Digits |
| 0.140 | Computer Music Journal | 2020 | Electronic_Khipu_: Thinking in Experimental Sound from an Ancestral Andean Interface |
| 0.128 | Journal of New Music Research | 2018 | Symbaline: An electromagnetically actuated wine glass instrument |
| 0.122 | Contemporary Music Review | 2019 | Choreography in R. Murray Schafer's The Crown of Ariadne—Technical or Theatrical? |
| 0.120 | Computer Music Journal | 1986 | Elementi di Informatica Musicale |
| 0.113 | International Conference on Live Coding | 2020 | Disabled Approaches to LiveCoding, Cripping the Code |
| 0.108 | Journal of New Music Research | 2002 | The Exbow MetaSax: Compositional Applications of Bowed String Physical Models Using Instrument Controller Subsititution |
| 0.107 | Contemporary Music Review | 2010 | The Real-Time-Score: Nucleus and Fluid Opus |
| 0.102 | Computer Music Journal | 2017 | Real-Time Timbre Classification for Tabletop Hand Drumming |
| 0.098 | Sound and Music Computing | 2022 | Espaces sonores paradoxaux : Approche des harmoniques hypersphériques et implémentation logicielle, pour une pratique créative de la spatialisation immersive du son en free-party |
| 0.095 | Sound and Music Computing | 2016 | Optical or Inertial? Evaluation of Two Motion Capture Systems for Studies of Dancing to Electronic Dance Music |
| 0.089 | Sound and Music Computing | 2004 | Three-dimensional Gestural Controller Based on Eyecon Motion Capture System |
| 0.089 | Computer Music Journal | 2015 | Expressive Robotic Guitars: Developments in Musical Robotics for Chordophones |
| 0.087 | Sound and Music Computing | 2020 | Resurrecting the tromba marina: A bowed virtual reality instrument using haptic feedback and accurate physical modelling |
| 0.087 | Computer Music Journal | 2015 | Designing Musical Instruments for the Browser |
| 0.087 | Sound and Music Computing | 2022 | Soutenir en Classe L'écoute Active, L'Autonomie Et L'échange en Analyse Musicale Avec la Plateforme Web Dezrann |
| 0.086 | Computer Music Journal | 1977 | Unplayed by Human Hands |
| 0.085 | Computer Music Journal | 1995 | 3-D Sound for Virtual Reality and Multimedia |

The fifth list comes from one round of snowballing. 126 of the 169 Cited works have reference lists in Crossref, and [`candidates_snowball.tsv`](output/candidates_snowball.tsv) holds the 120 works that at least 3 of them cite and that neither archive nor Cited holds. Proceedings and journal names are not counted as works, and a work cited both by DOI and by title is counted once.

| Cited by Cited works | Year | First author | Title |
|---|---|---|---|
| 12 | 2007 | Leman M. | Embodied Music Cognition and Mediation Technology |
| 8 |  |  | Musical gestures: Sound, movement, and meaning |
| 6 | 2015 | McPherson Andrew | An Environment for Submillisecond-Latency Audio and Sensor Processing on BeagleBone Black. In Audio Engineering Society Convention 138 |
| 6 | 2001 | P. Dourish | Where the action is: the foundations of embodied interaction |
| 6 | 1986 | Dolson | The Phase Vocoder: A Tutorial |
| 6 | 2000 | Lewis | Too Many Notes: Computers, Complexity and Culture in Voyager |
| 6 | 2003 | Gaver | Ambiguity as a resource for design |
| 6 | 2001 | Poupyrev | New interfaces for musical expression |
| 6 |  |  | Instruments and Players: Some Thoughts on Digital Lutherie. |
| 6 | 1954 | Fitts | The information capacity of the human motor system in controlling the amplitude of movement. |
| 6 | 2009 | G. Paine | Towards Unified Design Guidelines for New Interfaces for Musical Expression |
| 6 | 2003 | COLLINS | Live coding in laptop performance |
| 6 | 2010 | T. Bianco | Gesture in Embodied Communication and Human-Computer Interaction |
| 5 | 2009 | N.H. Rasamimanana | Effort-based Analysis of Bowing Movements: Evidence of Anticipation Effects |
| 5 | 2005 | Wright M. | Open Sound Control: an enabling technology for musical networking |

### Theses

PhD and master's theses were collected separately, since they dominate the forward list and are poorly covered by the journals. 36 NIME-related queries to OpenAlex (works of type dissertation) and DataCite (Dissertation and Thesis records), and a DataCite title lookup of the untyped works on the forward list, gave 6122 distinct theses, of which 366 are not in English and are listed separately for the non-English sources ([`candidates_theses_non_english.tsv`](output/candidates_theses_non_english.tsv)).

Thresholds borrowed from the journal sweep admitted too few theses, since thesis abstracts read differently from article abstracts, so the thresholds are calibrated on the 35 English theses known to cite the archives: closeness at their lower quartile and contrast at their median. With contrast at the lower quartile, a reading of sampled titles found many off-topic theses (music education, club culture, signal processing); with contrast at the median, few, which is why the median is used. As a check on a separate population, the searches found 9 of the 32 theses already in off-NIME, and the rules would admit 6 of them (66.7%). [`bibs/Theses/theses.bib`](../bibs/Theses/theses.bib) holds the 416 admitted theses, 37 of them because they cite at least three archive entries, and the website shows them under a Theses tab. The full scored list is [`candidates_theses.tsv`](output/candidates_theses.tsv).

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

1. Vet the Cited dataset and the borderline list. `bibs/Cited/cited.bib` holds 169 works admitted by fixed rules: each has a DOI, so its metadata comes from Crossref rather than from a parsed reference string; each is in neither archive; each is at least as close to the archives in wording as the lower quartile of the curated CMJ articles; and each is cited by at least 5 archive papers (82 works), cites at least 10 archive entries (107), or turned up in the journal sweep as well as on one of those lists (45). The website shows them under their own Cited tab. [`borderline.tsv`](output/borderline.tsv) lists 630 works with a DOI that fall short of one rule. Its top rows are clearly relevant reviews that miss the closeness bar only because their titles are short, so it needs a human reading. [ARJ: vet the top of the borderline list, and remove anything from Cited that does not belong.]
2. Use the forward list to continue off-NIME past 2013. Its top entries are mostly theses and journal articles that position themselves against NIME. The Crossref sweep gives a systematic list alongside the citation-driven one, and the two can be read together: an article that appears in both is a strong candidate.
3. Mine the local archive. ICMC 2000–2008 is present locally in full, and the score shortlists 229 ICMC papers. The full ICMC archive at the University of Michigan library, and ICMC's listing in DBLP, both sit behind bot checks, so they cannot be read by a script. [ARJ: ask the ICMA or Michigan Publishing for a metadata export of the ICMC proceedings (recommended), or extend the local copy year by year?]
4. Snowball. Each accepted candidate brings its own reference list; repeating the citation step until a round yields few new works cited by five or more archive papers would close the backward list.
5. Give every off-NIME entry a DOI or Semantic Scholar identifier, and an abstract where one exists. Topic modelling and citation matching both suffer most from titles-only entries. The Semantic Scholar title lookup is in `tools/fetch_s2.py` and resumes from its cache, but it needs an API key to finish in reasonable time. [ARJ: request a Semantic Scholar API key (recommended), or use OpenAlex's free daily allowance over several days?]
6. Decide where the result lives. The off-NIME site and the NIME bibliography share a format; a joined export with an `archive` field, as `data/corpus.json` already is, would let the NIME website show both. [ARJ: propose this to the IDMIL maintainers as a pull request (recommended), or keep it in this fork for now?]

### Exports

The joined collection, with the NIME proceedings, the off-NIME archive and the Cited dataset, is exported as [`collection.csv`](output/collection.csv) for spreadsheets and as CSL-JSON in [`collection.json`](output/collection.json), which Zotero, Mendeley and pandoc import directly. Each of its 4521 entries names its archive and dataset and, for archive entries, its strongest topic.

## Limitations

Author keys merge people who share a surname and initial, and split people who publish under different initials. The reference parser misses about half of the links that Semantic Scholar finds, so counts in the backward list are lower bounds and rank works by how often they are cited in papers whose text parsed well. The forward list depends on Semantic Scholar's coverage, which is better for recent work. Titles in the third list are guessed from first pages. The topic model is fitted on uneven text: abstracts for NIME, titles for off-NIME.

## Data and code

The scripts are in `analysis/tools/` and run from `analysis/.venv` in this order: `build_corpus.py`, `fetch_s2.py`, `fetch_citing.py`, `fetch_texts.py`, `extract_local.py`, `parse_refs.py`, `citations.py`, `crossref.py`, `local_candidates.py`, `score_journals.py`, `build_cited.py`, `offnime_dois.py`, `analyse.py`, `export.py`, `build_viewer.py` and `report.py`; `run.sh` runs them in that order. Downloaded texts and caches are in `analysis/data/` and are not committed. The atlas is `analysis/output/nime-atlas.html`; the candidate lists are the three `.tsv` files beside it.

## Contributor roles

Alexander Refsum Jensenius: conceptualisation, resources (the local conference archive), supervision. The NIME bibliography is maintained by the NIME community; the off-NIME archive was built at IDMIL, McGill University, under Marcelo M. Wanderley, by João Tragtenberg, Kasey Pocius, Maxwell Gentili-Morin and Ian Doherty.

## AI disclosure

The scripts, the analysis and the draft of this report were produced with Claude Opus 5.5 (Anthropic) in Claude Code, working from the instructions of the author. Paper metadata and citation links come from the Semantic Scholar Academic Graph API.
