# Voice-first UI research for low-literacy users

**Read this if…** you want the evidence behind the voice-first rules in [design/voice-first.md](../design/voice-first.md).

Frozen report, 13 Nov 2026. Desk research by an AI research agent for Yahya. Not user research: no farmers were asked or observed.

---

## Method and limits

Web search across HCI4D/ICTD papers, platform design guidelines and engineering threads. Paper PDFs could not be opened; most findings come from abstracts, search snippets and official guideline pages. Numbers are quoted only where a snippet gave them, and one is flagged as second-hand. Evidence labels: **[study]** measured result · **[guide]** official platform guidance · **[opinion]** practitioner view · **[inference]** our reasoning, not a source.

## Findings that shaped the plan

| # | Finding | Evidence |
|---|---|---|
| 1 | Novice rural users did better with keypad than open speech, especially with less schooling. A secondary summary gives 74% vs 61% completion (unverified). | [study] [Patel et al., CHI 2009](https://hci.stanford.edu/publications/paper.php?id=68) |
| 2 | Graphical UI had the highest completion (reported 100% vs 72% for spoken dialog); people who understood the spoken system were faster with it. | [study] [Medhi et al., TOCHI 2011](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ToCHI2711_Medhi.pdf) |
| 3 | Rich multimedia gave better completion; spoken dialog was faster and needed less help. | [study] [Medhi, Gautama, Toyama, CHI 2009](https://microsoft.com/en-us/research/wp-content/uploads/2016/02/medhi_chi2009.pdf) |
| 4 | Conflicting result: a well-designed speech system (HealthLine) beat touch-tone for literate and low-literate users once they had guided tutorials. Recognizer quality and training decide it, so keep both inputs. | [study] [Raza, 2021 chapter](https://aghaaliraza.com/publications/2021--DevEnggBook--Voice_Interfaces_for_Underserved_Communities.pdf) |
| 5 | Tap-to-hear on every message helped farmers (34 farmers, Jharkhand). Semiliterate users cut audio use over time; illiterate users did not. | [study] [FarmChat, IMWUT 2018](https://ubicomplab.cs.washington.edu/publications/farmchat), [Findlater et al., CHI 2009](https://www.dgp.toronto.edu/public_user/ravin/papers/chi2009_literacy.pdf) |
| 6 | Text-free designs with simple graphics and voice feedback were preferred; a consistent help button was an overlooked need. | [study] [Medhi et al., 2007](https://www.microsoft.com/en-us/research/?p=160568) |
| 7 | Screen must match what the voice says; show the words when every word matters. | [guide] [Alexa multimodal](https://developer.amazon.com/en-US/blogs/alexa/alexa-skills-kit/2018/12/how-to-design-visual-components-for-voice-first-alexa-skills) |
| 8 | Confirm implicitly (restate and move on); explicit yes/no only before hard-to-undo actions. | [guide] [Google confirmations](https://developers.google.com/assistant/conversation-design/confirmations?hl=en) |
| 9 | On recognition errors: brief reprompt with an example; stop after two no-matches. | [guide] [Google errors](https://developers.google.com/assistant/conversation-design/errors) |
| 10 | Keep spoken responses short; each must stand alone without the screen. | [guide] [Apple HIG: Siri](https://developer.apple.com/design/human-interface-guidelines/siri) |
| 11 | Novices listen to whole prompts; barge-in grows with experience. | [study] [Raza et al., DEV 2013](https://aghaaliraza.com/publications/2013--DEV--%20Behavior_Analysis_of_Low-literate_Users_of_a_Viral_Speech-based_Telephone_Service.pdf) |
| 12 | Permission prompts without user intent are allowed far less often (Chrome telemetry: 12% vs 30% after interaction). Ask for the mic on first use. | [guide/telemetry] [web.dev permissions](https://web.dev/articles/permissions-best-practices) |
| 13 | People learn voice by doing: guided tutorials (HealthLine), a voice game (Polly), trained facilitators (Egypt's GeoAgro-MiSR). | [study] [Polly, CHI 2013](https://aghaaliraza.com/publications/2013--CHI--Job_Opportunities_through_Entertainment.pdf), [programme] [ICARDA](https://ftp.icarda.org/node/18698) |
| 14 | 65% of Avaaj Otalo users wanted answers only from the NGO's experts: say who stands behind the content. | [study] [Patel & Savani, ICTD 2012](https://cs.stanford.edu/~neilp/pubs/ictd2012_patel.pdf) |
| 15 | Users given IVR menu instructions often "just start talking" instead of pressing keys. | [study] [Raza, CHI 2013 extended](https://aghaaliraza.com/publications/2013--CHI--Job_Opportunities_through_Entertainment--Extended.pdf) |
| 16 | Farm audio is noisy (machinery, media, other speakers) and farm vocabulary trips general recognizers. | [study] [Digital Green, arXiv 2609.20504](https://arxiv.org/pdf/2609.20504), [arXiv 2602.03868](https://arxiv.org/pdf/2602.03868v2) |
| 17 | Option lists of about four or fewer for voice. | [opinion] [uxdesign.cc](https://uxdesign.cc/design-tips-for-alexa-multimodal-devices-6eb1c6ce134e) |

## Browser speech on Android Chrome (our planned stack)

- **No on-device Web Speech on Android** (Chromium, May 2026). Recognition goes over the network and fails offline. [primary] [blink-dev thread](https://groups.google.com/a/chromium.org/g/blink-dev/c/P8P-x7AnC6I)
- **Continuous listening is unreliable on Android** (mic cycling, duplicate results, a start beep). Anecdotal developer reports. [forum] [react-speech-recognition issue](https://lightrun.com/answers/jamesbrill-react-speech-recognition-react-speech-recognition-does-not-work-in-chrome-for-mobile)
- **`speechSynthesis` on Android may silently fall back to English** when the language pack is missing. [docs] [Readium WebSpeech](https://readium.org/speech/docs/WebSpeech.html)
- **Egyptian Arabic TTS is under-served**; most Arabic TTS targets MSA or Gulf. [literature] [arXiv 2602.15675](https://arxiv.org/html/2602.15675v1)
- **No current independent accuracy figure for Google's ar-EG recognizer** was found. A 2015 paper reports roughly 34 WER on an Egyptian test set (PDF not opened). [study, old] [Columbia 2015](https://www.cs.columbia.edu/speech/PaperFiles/2015/dialect_challenges.pdf)

**[inference]** Because spoken content comes only from fixed templates, pre-recorded human Egyptian Arabic audio avoids both the TTS fallback and the dialect problem. Keep recognition to small vocabularies (crops, months, numbers, yes/no) and test on real Android phones near Sakha before relying on it.

## Not covered

No primary sources found for Kisan Call Centre, Project Vaani, Jio voice features or Gemini Live design; no measured study on progress indicators for non-readers.
