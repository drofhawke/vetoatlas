# Methodology

*Translated from the Turkish original (METODOLOJI.md). Where the two differ, the Turkish text
prevails.*

This document is published together with the platform. Every figure and every claim rests
on the rules set out here; if a rule changes, the document is versioned.

## 1. Categories

The platform uses three separate categories and never mixes them.

**Formal veto:** A permanent member's negative vote on a draft resolution that would otherwise
have received the required votes. Main source: the Dag Hammarskjöld Library veto list
(for 1946–2004 based on UN document A/58/47, Annex III).

**Hidden veto:** Drafts not put to a vote, or watered down, because of a veto threat. They are
recorded only if documented in a primary source (meeting record, official statement) or a
recognised independent source (e.g. Security Council Report).

**Inaction:** The Council's failure to take a decision in the face of a crisis, or its narrowing
of an existing mandate. Example: Rwanda 1994. These cases are not presented as vetoes.

## 2. Counting rules

The "number of vetoes" is calculated in two ways, and both are always given together. The count
by draft is the number of draft resolutions that failed because of a veto. The count by vote is
the number of negative votes cast; if two members vetoed one draft, it counts as 2. Council size:
eleven members and the rule of seven affirmative votes until 31 August 1965, when the 1963
Charter amendment entered into force; fifteen members and nine votes thereafter. As no veto was
cast between 31 August 1965 and the end of 1965, the dataset counts records before 1966 under the
eleven-member Council ("ten against one" in the "fourteen against one" gallery, threshold 7 on
the simulation page). Vetoes of
paragraphs or amendments, marked with an asterisk in the source, are flagged separately.

Vetoes of the USSR belong to the seat to which the Russian Federation succeeded, but are coded
separately. "China" vetoes before 25 October 1971 belong to the Republic of China (Taiwan) and
are not attributed to the People's Republic of China.

### 2.1. Early records (1946–1953)

For some vetoes in this period the draft resolution was not issued as a separate S/ document;
the proposal was made directly at the meeting and appears in the meeting record. These records
are not treated as missing data; they are flagged `taslak_kaynagi: toplanti_kaydi`.

The source uses the asterisk in two different senses. Mostly it marks a partial veto of a
paragraph or an amendment. In private meetings (e.g. the appointment of the Secretary-General)
it shows that the vetoing member is not named in the official communiqué and that the
attribution is the source's. The two are kept in separate fields.

A partial veto is a negative vote cast in a separate vote on an amendment or on a part of a
draft (a paragraph, a sentence, a word) rather than on the draft as a whole. The asterisk in the
source, the "oral amendment" entry and the "kismi" column of `duzeltmeler.csv` set this flag.
14 of the partial vetoes come from the membership package of 13 December 1955: the Council voted
one by one on the country names in the second preambular paragraph of the draft of Brazil and
New Zealand (S/3502); 13 words failed on the negative vote of the USSR and "Mongolian People's
Republic" on that of the Republic of China (S/PV.704, paras. 54 and 57–72). The definition also
covers the words and paragraphs of a draft voted on separately; this is consistent with the scope
of Part II of A/58/47 Annex III ("Paragraphs of draft resolutions or amendments thereto not adopted
owing to the negative vote of a permanent member"), which lists these votes as "Preambular para. 2
(the word ...)". All 16 records of 13 December 1955 (the 14 word votes and the two parts of the
Chinese amendment S/3506) are partial vetoes; the word votes are linked to draft S/3502, the
amendment votes to S/3502 and S/3506.

"Preliminary question" vetoes are vetoes cast in the vote on whether a matter is to be considered
procedural (the double veto). Since there is no veto on procedural decisions, a permanent member
that first vetoes this preliminary question opens the substantive matter to a veto as well.
These records are flagged separately.

Lines that appear more than once on the same day, under the same agenda item and with the same
content are listed by the source as separate vetoes. They are not deleted; they are told apart
by checking the meeting record.

### 2.2. Source reconciliation

The main data source is the DHL veto list; document numbers and links come from it. The accuracy
of the count is ensured by comparing it line by line with the veto table of Sievers and Daws,
*The Procedure of the UN Security Council*, the standard reference work on Council procedure
(scprocedure.org, Table 4).

Every difference between the two sources is recorded with its reason in
`kaynaklar/duzeltmeler.csv`, and no correction is embedded in the code. Every added or changed
record carries in its `duzeltme` field the reference line on which it rests.

The reconciliation found 18 proposals missing from the DHL list: 16 vetoes on 13 December 1955
(15 membership and amendment vetoes by the USSR and the Republic of China's veto of Mongolia),
the joint China–USSR amendment veto of 10 September 1972, and two separate Russian vetoes of
24 February 2025 merged into a single line. In addition, a negative vote cast by France together
with the USSR on 26 June 1946 is missing from the DHL list.

The vetoes of 13 December 1955 and 10 September 1972 have been verified from the meeting records
(S/PV.704 and S/PV.1662, `kaynaklar/.belgeler/`). The vote breakdowns and the vetoing
members are the same as in the reference table. The order within the day in the reference table
differs from the order at the meeting: the Mongolia veto is the 3rd of the 16 vetoes at the
meeting (No. 76 in the table, the last entry of the day); the 1972 amendment veto was voted
before the US veto at the same meeting (No. 118 US, No. 119 amendment in the table). As the table
does not state the rule by which it orders entries within a day, this is not counted as an error.
Under Rule 2 in 2.3 record identifiers are not changed; the order at the meeting is written in the
notes.

The DHL list states that its data for 1946–2004 are taken from A/58/47 Annex III. These 17 vetoes
are in Part II of that annex (vetoes of paragraphs and amendments), and the list includes other
entries from the same part; their absence is therefore an omission rather than a difference of
scope, and it is included in the error report (`kaynaklar/KAYNAKLAR.md`, "[DHL listesinin kapsamı]{lang=tr}").

The dates in the two sources differ for seven vetoes. These differences are not deleted. The
voting day is determined from the meeting record, and the record uses the date given by
whichever source is correct; the other source's date remains in the notes. Internal
inconsistencies of the reference source (`kaynaklar/KAYNAKLAR.md`) are documented in the same
way.

The overall vote (in favour–against–abstaining) is taken from the reference table. Where there
is more than one veto under the same agenda item on the same day, matching is done by country
name, agenda item or a footnote in the source, and the reason is written into the record. Those
that cannot be matched in these ways are left empty until matched by hand from the meeting
record; no guess is made.

The coverage of the reference table ends with the veto of 18 September 2025. Vetoes after that
date are added and verified from UN primary sources: the draft resolution (S/…), the meeting
record (S/PV.…) and the UN press release. The vetoing members, the vote and the agenda item are
taken from the voting section of the meeting record. For vetoes that are in the DHL list but
have no vote breakdown (7 April 2026, S/2026/273), the vote is added in this way. Vetoes that are
not in the canonical DHL file (17 September 2026, S/2026/740) are recorded from the same
sources. These lines are kept in `duzeltmeler.csv` with the `kaynak_url`, `oy` and `taslak`
columns, and with the page number of the meeting record in the reason. In the reconciliation
they are added to the reference totals as "after coverage". A detail that could not be verified
(e.g. a press release that could not be opened) is stated explicitly in the reason.

**Verification from meeting records.** Records on which the two sources disagree, or for which
neither is sufficient on its own, are verified from the meeting record (S/PV) itself. Records
are opened as PDFs of the UN document system through undocs.org. For older years the Official
Records version (S/PV.NNNN(OR)) is used; scanned pages without a text layer are read from the
image. The vote breakdown is counted from the lists of countries voting in favour, against and
abstaining in the record. The voting day is derived from the opening and closing times of the
meeting, from suspensions and from time references in the statements ("yesterday morning",
"tomorrow, 7 September"). If the meeting ran past midnight, these indications are used to tell
on which day the vote took place, and this is noted. The record identifier (V-<DHL date>-n)
does not change even if the date is corrected. Lines that are identical in the DHL list are
assigned in the order of the votes at the meeting. Every finding is kept in `duzeltmeler.csv`
with the meeting record and the PDF page number (`oy_esle`, `tarih_dogrula`). Where a value
conflicts with the reference table, the meeting record prevails and the conflict is written into
the record. If the record cannot be reached, or does not give a definite result, no guess is
made: the record is left as "could not be verified" with the reason, and the "Under
verification" label stays in the interface. Access barriers such as CAPTCHAs or bot checks are
not circumvented.

**Citation rule.** Where the meeting record has paragraph numbers, the primary citation is the
paragraph number; the PDF page stays beside it in parentheses ("S/PV.704, para. 54 (PDF p. 13)").
Records without paragraph numbers are cited by PDF page; where the printed page differs from the
PDF page, the difference is stated. Documents that are not in the document system or whose
automated access is blocked are kept locally (`kaynaklar/.belgeler/`, `kaynaklar/KAYNAKLAR.md`,
"Yerel belgeler") and do not enter the repository.

**AI output is never a source.** A summary, translation, transcript or list produced by a language
model is not used in place of the source itself and is not placed in the repository as a source.
Every piece of information is taken from the document itself (meeting record, draft resolution,
official list) and cited to that document.

Document links in the interface and in the open data are built from document symbols
(`https://undocs.org/<symbol>`); the links on the DHL page are not used, because five of them
are broken (`kaynaklar/hata_bildirimi.md`, message to DHL). The raw links remain under
`data/processed/` as they appear in the source. The format of document symbols and links is
checked by `tests/test_belge_kodlari.py`; no requests are sent to the links.

### 2.3. Date and identifier rules

**Rule 1: The date of a veto is the calendar day on which the vote actually took place.** For
meetings that ran past midnight, this day can differ from the date in the heading of the meeting
record (the day the meeting opened). Examples: 3/4 December 1960, 20/21 February 1961,
22/23 August 1968. Both dates are kept in the record. The voting day is in the `tarih` field.
The date given by the source is in `tarih_ham`, the reference table's in `referans_tarih`. The
heading date of the meeting record and how the voting day was determined are written, with
page numbers, in the notes and in the `toplanti_dogrulamasi` field.

**Rule 2: Record identifiers are permanent keys and carry no date information.** The identifier
(`V-YYYY-MM-DD-n`) is generated when the record is first created, from the DHL date and the
order within the day. The date part shows only that initial moment; it is not read as a date,
and the date is taken only from the `tarih` field. If a record's date is later corrected, its
identifier does not change. For example, the date of V-1950-09-05-1 is 1950-09-06. Because
correction files, topic corrections and external links depend on the identifier, changing it
would break these links.

### 2.4. Topic classification and Turkish titles

Each veto is assigned exactly one of 15 topics as its main topic: Palestine and the Arab–Israeli
conflict; Lebanon; Syria; Other Middle East and North Africa; Cyprus; Ukraine; Other Europe;
South Africa, Namibia and Rhodesia; Other Africa; Latin America and the Caribbean; Asia;
Disarmament and military incidents; Membership applications; Appointment of the
Secretary-General; Thematic issues.

The assignment has two layers. `kaynaklar/gundem_sozlugu.csv` gives, for each of the 136 unique
agenda titles in the dataset, a faithful Turkish translation, a topic and a region. No
interpretation is added to the translation; date, sender and document number are rendered as
they are. Where the title alone is not enough, the topic comes record by record from
`kaynaklar/konu_duzeltmeleri.csv`. For example, vetoes under the general title "The situation in
the Middle East" may concern Lebanon, Syria or Palestine. The reason for each line in this file
is the subject given to that veto in scprocedure Table 4. For vetoes outside the table's
coverage, the reason is the subject of the draft and the meeting record.

If a veto touches more than one topic, the topics other than the main one are written into the
`ikincil_konular` field. Examples: Palestine for the 2024 Palestine membership veto and the 1956
Suez vetoes, Other Middle East for the 1958 Lebanon–Jordan complaint. A secondary topic also
links the record to that topic in filtering, but does not enter any count. Topic totals count
only the main topic and always add up to 266 proposals. In the interface, secondary links are
shown in a separate note.

When a new title arrives that is not in the dictionary, the data pipeline issues a warning and
sets the record's topic to "Unclassified"; no topic is assigned by guesswork. The record appears
with this label until a dictionary line is added.

### 2.5. General Assembly debates (A/RES/76/262)

Under A/RES/76/262, adopted on 26 April 2022, the President of the General Assembly convenes a
debate within 10 working days after every veto. If the General Assembly meets in an emergency
special session on the same situation, no separate debate is held. The Security Council, for its
part, submits a special report for every veto. Vetoes before that date are outside the scope of
this section; no General Assembly section is shown for them in the interface.

Debates are kept separately from vetoes in `kaynaklar/genel_kurul_tartismalari.csv`. One debate
can cover several vetoes, and one veto can be covered by several debates. The Council's special
reports are in `kaynaklar/ozel_raporlar.csv`. There are two kinds of debate: `veto_girisimi`
(the debate under the agenda item "Use of the veto") and `olaganustu_ozel_oturum` (ES-10,
ES-11). Speakers are not counted for emergency special sessions; only the meeting records and
the resolutions adopted are listed.

**Record status.** One of three values is used for each meeting record. `resmi`: verbatim record
published in the UN document system (A/…/PV.…). `gayriresmi_transkript`: verbatim record not
published, but the UN's automatic speech-recognition transcript (transcripts.un.org) exists.
`yayimlanmadi`: neither exists. Every piece of information taken from an unofficial transcript
is flagged separately in the `gayriresmi_alanlar` column. Pending records are checked with
`scripts/05_bekleyen_kayitlar.py`; a record that is published is processed by hand, and if
necessary the count is redone from the verbatim record.

**Verification.** The date and agenda of each debate are verified from an official source: the
verbatim record or the Journal of the United Nations (journal.un.org). If the Journal shows that
the meeting took up an agenda linked to the veto in question (the agenda item, the special
report or the letter reconvening the session), the record becomes `dogrulandi` and the basis is
written in the `dogrulama_kaynagi` column.

**Speaker counting rules** (veto initiative debates only):
- Only statements under the veto agenda item are counted. Other items taken up at the same
  meeting, and continuation meetings of the debate, are separated by the agenda item headings
  in the verbatim record.
- Each delegation is counted once. The President and the Secretariat are not counted.
- A delegation speaking on behalf of a group counts as one speaker. That it spoke on behalf of a
  group is marked, with the group's name, in the `grup_adina_konusanlar` column. The group mark
  comes from two sources: the Journal's "on behalf of" note and the speaker's own statement in
  the verbatim record ("I speak on behalf of …"). Aligning with or supporting another
  delegation's group statement, speaking on behalf of one's own country, and general phrases
  such as "on behalf of all Member States" are not counted as group statements.
- Observers (European Union, State of Palestine, Sovereign Order of Malta, etc.) are counted in
  a column separate from Member States.
- Rights of reply are kept separate from statements.
- `veto_eden_konustu` is kept separately for each vetoing country; for double vetoes both
  countries are listed. Values: `aciklama`, `yalnizca_cevap_hakki`, `hayir`.
- Source: for debates whose verbatim record has been published, the count is made from the
  verbatim record and compared with the Journal summary. For debates whose verbatim record has
  not been published, the count is made from the Journal summary; `konusmaci_kaynagi` shows
  this. The debate summaries published by the Office of the President are used for cross-checks.
  Every figure that does not match is written in the `capraz_kontrol` column.
- Control figure: in the debate of 6 March 2025 (A/79/PV.60), 35 delegations made statements
  (34 Member States and the European Union). This figure is the same as in the President's
  summary.

### 2.6. English version and translations

Notes, correction reasons and topic reasons are written in Turkish; the Turkish text is the
original. The English counterpart of each is kept alongside it: `aciklama_en` in
`kaynaklar/duzeltmeler.csv`, `gerekce_en` in `kaynaklar/konu_duzeltmeleri.csv`, and
`kaynaklar/notlar_en.csv` for the fixed notes produced by the parser. The English names of the
topics are in `kaynaklar/konular_en.csv`. Translations are faithful: document symbols, page and
paragraph numbers, the numbers in dates and proper names are not changed. If a phrase whose
original English wording has not been verified is given in quotation marks in the Turkish, it is
rendered without quotation marks in English, so as not to create an invented quotation. If the
English of a note is missing, `04_web_verisi.py` issues a warning and the English version of the
interface shows the Turkish original of that note. In the English version, agenda titles are
given in their original UN wording. The English text of this document is in `METODOLOJI_EN.md`;
the page `web/metodoloji.html` is generated from both each time `04_web_verisi.py` runs.

### 2.7. Quotation bank and the Word and Record page

`kaynaklar/alintilar.csv` holds quotations from President Recep Tayyip Erdoğan's addresses to the UN
General Assembly in 2019 and 2022-2026 and from the book *A Fairer World is Possible* ([*Daha Adil Bir Dünya Mümkün*]{lang=tr}). The sources
are not in the repository; their bibliographic details and SHA-256 values are in
`kaynaklar/KAYNAKLAR.md`. Quotations are cut from the PDF text layer, and each is searched for word
for word, with whitespace normalised, on the page given. For the addresses, the printed page and
the PDF page are both kept. Because the Turkish PDF of the book carries no printed page numbers, no
page number is given for the Turkish text of book quotations; they are attributed by chapter title. If a
quotation cannot be verified, `04_web_verisi.py` stops. When a quotation is shortened with an ellipsis (…),
each part separated by the ellipsis is searched for separately and word for word in the source; the parts
must come in the source's order and from the same passage. The quotation bank keeps the full text; the
shortened form is used only in the story (the opening quotation and step 7). The story's opening quotation
comes from the 2019 address: in Turkish, the sentence [“Dünya 5’ten Büyüktür.”]{lang=tr} from the Turkish
booklet; in English, "The world is bigger than five!" from the English booklet.

The English pages use the official English text of each quotation; the atlas does not translate quotations.
The official English text follows the same rule as the Turkish text: it is searched for word for word on the
page given in its own source, `04_web_verisi.py` stops if it cannot be verified, and the tests
(`tests/test_alintilar.py`) check every English text whose source is available locally against that source.
The sources are:
- 2022–2026 addresses: the English section of the compilation.
- 2019 address: the English booklet of the Directorate of Communications. The booklet is the prepared text of
  the speech. For the passage added at the rostrum that is not in the booklet (2019-2), the English is taken
  from the UN's English meeting record (A/74/PV.3). The speech was delivered in Turkish; the English in the
  record is the interpretation provided by the delegation.
- The book: the English edition, *A Fairer World is Possible* (Turkuvaz Kitap, 2021), with printed page
  numbers and English chapter titles. The PDF of the English edition is a scan with an OCR text layer, so the
  pages holding the quotations were compared with the page images. The single place where the OCR differs
  from the image (an en dash on p. 32) is corrected to match the image before the search
  (`kaynaklar/KAYNAKLAR.md`).

Where no official English text can be found, the English page keeps the Turkish original and adds below it a
translation labelled "Unofficial translation by Veto Atlas". Such a translation is not verified against a
source. At present every quotation has an official English text.

The Word and Record page (`web/vizyon.html`) places next to each quotation a corresponding figure computed from the dataset.
Figures are computed when the page loads; no causal link is drawn between a quotation and a
figure. "Vetoes related to Gaza since October 2023" are vetoes with a voting day on or after
7 October 2023 whose draft text contains the word "Gaza" (`kaynaklar/gazze_taslaklari.md`). In this list, the veto of 22 December 2023 concerned not the draft
itself but an oral amendment to it; the `veto_hedefi` column records this, and 04 checks the flag
against the "oral amendment" note in the record. In "The model in the book" section, quotations are kept short
and the rest of each element is summarised.

The regional distribution uses the region field of the agenda dictionary: Middle East and North
Africa, Europe, Africa, Asia and the Pacific, Latin America and the Caribbean, and Global. "Global"
covers agenda items not tied to a particular region (general membership applications,
disarmament, appointment of the Secretary-General, thematic issues). The region is assigned from
the agenda title and is independent of the topic classification. The numbers of delegations in
veto initiative debates are the counts made under the rules in 2.5 (member states and observers
together; rights of reply excluded).

### 2.8. Reform models

The Reform models page (`web/reform.html`) sets four models for Security Council reform side by side against
the same four criteria: total membership, new permanent members, who holds the veto, and the relationship with
the General Assembly. The models are the Ezulwini Consensus (Ext/EX.CL/2 (VII); A/59/L.67), the G4
(A/59/L.64), Uniting for Consensus (A/59/L.68) and the book *A Fairer World is Possible*; they are given in
the date order of the documents. The comparison is taken from the primary documents
(`kaynaklar/reform_modelleri.csv`): each cell summarises the document's own provision, and the paragraph
relied on is given under it. Every phrase quoted from the book is found word for word in a verified quotation
in the quotation bank (tested); as the book has no page numbers, the basis is the chapter title. The page
makes no evaluative statement about the models.

### 2.9. Representation index

`web/temsil.html` shows five shares side by side for the UN regional groups; the computation is
`scripts/09_temsil.py`, the inputs `kaynaklar/temsil/*.csv`, the output `data/processed/temsil.json`.
Nothing is added to the veto dataset; there is no composite score or ranking.

- **Unit:** the UN regional groups (DGACM list, 10 October 2026). Türkiye is listed in two groups and is
  counted only in WEOG for electoral purposes; the United States is not a member of any group and is
  counted in WEOG for electoral purposes. Both are counted in WEOG and noted. Geographical regions (M49)
  are not used; the seat distribution rests on the electoral unit.
- **Population:** WPP 2024, estimate as of 1 January, thousands; years 2023 (last estimate year) and 1963
  (the year of A/RES/1991 (XVIII)). There is no WPP series for 1945; it is not computed. The 2023 share is
  within the total of the 193 members (non-member countries and areas, e.g. Palestine, Taiwan, Kosovo, Western Sahara and Puerto Rico, are not in the
  denominator). The
  1963 share is computed with the 113 members at the end of 1963 and their countries of that time: states
  that dissolved as the sum of their successors' series (USSR 13 republics, Ukraine and Byelorussia separate
  members; Yugoslavia 7 series; Czechoslovakia 2), states that were larger in 1963 with their borders of
  that time (Pakistan + Bangladesh, Malaysia + Singapore, Ethiopia + Eritrea, Sudan + South Sudan); with the
  China seat held by the Republic of China, the population is "China" + "China, Taiwan Province of China".
  Every successor rule is noted in the JSON; no series is counted twice (tested).
- **Membership share:** members in the group / 193. **Budget share:** sum of the 2025–2027 regular budget
  scale percentages / 100 (A/RES/79/249; Committee on Contributions Excel). **Personnel share:**
  peacekeeping uniformed personnel (troops, police, experts, staff officers), country ranking as of
  28 February 2026 / grand total.
- **Seats:** permanent seat share = permanent / 5; total seat share = (permanent + elected) / 15, current
  term (UN Council members page, 2026). Distribution of elected seats: A/RES/1991 (XVIII) A para. 3
  (African and Asian 5, Eastern European 1, Latin American 2, Western European and other 2); the Africa 3 /
  Asia-Pacific 2 split is current practice. For each indicator the seat/indicator ratio = total seat share /
  indicator share; a ratio of 1 means the group's seat share equals its indicator share, above 1 the seat share
  is higher, below 1 it is lower.
- **Sets:** the five permanent members and the OIC members (of 57, Palestine is not a UN member; 56
  members). As the OIC was founded in 1969, the 1963 value is the sum of today's members that were UN
  members at that time, with their 1963 borders.
- **Sources:** population: United Nations, Department of Economic and Social Affairs, Population Division (2024),
  World Population Prospects 2024, Online Edition, `WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx`, licence
  CC BY 3.0 IGO; Member States and dates of admission: un.org/en/about-us/member-states; regional groups: DGACM,
  Regional groups of Member States, un.org/dgacm/en/content/regional-groups; scale of assessments: Committee on
  Contributions, `Scale of Assessments for RB 1946-2027.xlsx` (A/RES/79/249, 24 December 2024); peacekeeping: UN
  Peacekeeping, Uniformed Personnel Contributing Countries by Ranking, As of: 28/02/2026
  (`02_country_ranking_95_february_2026.pdf`); OIC members: oic-oci.org/en/members (57 members); Council members:
  UN Security Council, Current Members, main.un.org/securitycouncil/en/content/current-members; distribution of
  elected seats: A/RES/1991 (XVIII), 17 December 1963. All accessed 10 October 2026; references and SHA-256 values
  are in `kaynaklar/KAYNAKLAR.md`.
- **Language:** the page gives shares; it makes no comparative or evaluative statement.

### 2.10. The "What if there were no veto?" page

`web/simulasyon.html` counts the recorded votes of a veto record under two systems; no vote is
changed, added or guessed. Only records in the dataset can be selected; no hypothetical proposal can be
entered, and the page does not favour any model. When the 20-member Council of the book is selected, the computation still
relies only on the recorded votes, and the ratio of the selected threshold is kept: the current
majority rule of 9 out of 15 becomes 12 out of 20, two thirds 14 and a simple majority 11. If the
recorded yes votes alone meet this threshold, the outcome is "would have been adopted"; if not, the
outcome is given as "depends on the new members' votes", together with the minimum number of yes
votes needed from the 5 (before 1966, 9) members not on record. The votes of these members are not
guessed; a record that would not reach the threshold even if all of them voted yes is counted as
"would not have been adopted". The figures in the aggregate view are computed from the dataset when
the page loads. The box comparing the other models uses the provisions of the documents in 2.8; the paragraph
relied on for each is given in the box.

## 3. Language of causation

The platform does not claim that a veto "led to" particular outcomes. Case studies are presented
in the frame of "what happened in the period following the blocking of the draft" and contain no
counterfactual certainty. Humanitarian data (casualties, displacement, access to aid) are taken
only from published figures of UN agencies and recognised independent institutions; where a
range is given, the range is shown.

## 4. Scope and selection

The dataset includes every veto in the source without exception; no selection is made by
vetoing country or by topic. Vetoes taken up for in-depth case studies are selected by the
following criteria, and the criterion is stated for each selected case: the scale of the
humanitarian dimension, the number of votes the draft received, and repeated vetoes on the same
file.

## 5. The vetoing party's reasons

In each case study, the vetoing member's own statement in the meeting record is summarised. For
vetoes after 2022, the record of the mandatory General Assembly debate is linked.

## 6. Reproducibility

Every data version includes a dated raw copy of the downloaded source and its SHA-256 digest. The
parsing code is open; anyone can produce the same result from the same source. Error reports
are accepted, and corrections are entered in the change log.
