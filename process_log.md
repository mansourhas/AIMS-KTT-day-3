# Time log:
- [10:00 - 10:25] setting up the project and reading the doc.
- [10:30 - 11:50] trying to create the syntaic data
- [12:15 - 12:50] the tutor model, i chosed Phi-3-mini-4k, but it is not an ideal choice.
- [1:12 - ] pracrice for presentation.


# AI usage Log:
I'm using gemini fast and pro chat interface for Questions, Ideation and Coding. also i'm planning to use codex for coding tasks. 

## [sample 1] 
i used gemini to create a todo list for me to make sure i'm not missing any mildstone within the task. 

the prompt: `this challange is quite can't understand it , and not organized coherently, devided it into clear bits, and explain and note me on potenaila issues and how to proiortize`

the results are here, https://gemini.google.com/share/f92f940c0325
and also i'm adding it to Docs/tasks.md

## [Sample 2]
This shows the AI tendensy to give me full code with low quality and how i'm trying to improve the qulaiyt.

This conversation contain all the discrion with ai to build the code:
https://gemini.google.com/share/c1997b0c299d


## [Sample 3]
Ideation and verfication what have i missed about the project, and where can i improve my ratings.
prompt (with all my code files as context):`give me exact tips for best video recording experiance, i want the judges to see my techniqual ability and how my decision making thinking is`

respond: https://gemini.google.com/share/2c7e7c871182

# Hardest decision i made:

- for the Visuals
- also, for the TTS, While gTTS was sufficient for French and English, it lacked native support for Kinyarwanda, forcing a phonetic Swahili fallback. I judged this unacceptable for an early learner context where linguistic accuracy is critical. I traded off the increased local disk space and VRAM requirements to deploy Meta's facebook/mms-tts-kin via Hugging Face. This ensures culturally accurate Kinyarwanda pronunciation, which is then dynamically pitch-shifted to simulate a child's voice. 
