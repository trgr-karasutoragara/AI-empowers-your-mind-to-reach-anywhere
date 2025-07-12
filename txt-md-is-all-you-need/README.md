# .txt/md Is All You Need: A Terminal-First, AI-Powered e-Book Companion
## About this project

<img src="https://github.com/trgr-karasutoragara/AI-empowers-your-mind-to-reach-anywhere/blob/main/txt-md-is-all-you-need/sample/img/Screenshot-2025-07-12%2023.10.28.png" width="400">

```
api This situation must have been so difficult in times when there was no treatment available. 
```
```
You're right. The passage vividly illustrates the psychological torment that
accompanies a debilitating and disfiguring illness, especially when there's no
hope of a cure.  伯牛's (Bo Niu's) physical suffering is amplified by his fear
of rejection, his self-pity, and his growing resentment towards those around
him, even his revered teacher, Confucius.  The absence of modern medicine
makes his plight all the more tragic, as he is left to grapple with his pain
and despair without any real means of alleviating them.  It highlights the
importance of empathy, support, and human connection, especially for those
facing immense challenges.  The internal struggle he is going through is
palpable, and the lack of a medical solution makes it all the more poignant.
* Gemini 2.0 Flash via API
```

<br>

This is a prototype tool for reading .txt or .md files in the Ubuntu terminal, taking notes, and interacting with open-source LLMs or API-based LLMs while reading.
It is released under the MIT License, so I hope you enjoy extending its functionality.
The demo uses public domain texts from Aozora Bunko, but it also supports English as shown below.
Because the system is simple, it should be adaptable to any language you need.

<br>
<br>

<img src="https://github.com/trgr-karasutoragara/AI-empowers-your-mind-to-reach-anywhere/blob/main/txt-md-is-all-you-need/sample/img/Screenshot-2025-07-12-23.25.55.png" width="400">

<br>

### The following commands have been implemented

<img src="https://github.com/trgr-karasutoragara/AI-empowers-your-mind-to-reach-anywhere/blob/main/txt-md-is-all-you-need/sample/img/Screenshot-2025-07-12%2023.07.34.png" width="400">

<br>

### The basic interface displays the text in the terminal, with a command input field at the bottom

<img src="https://github.com/trgr-karasutoragara/AI-empowers-your-mind-to-reach-anywhere/blob/main/txt-md-is-all-you-need/sample/img/Screenshot-2025-07-12%2023.07.25.png" width="400">

<br>

### Since it only requires running a single Python file, you can also connect via SSH from a Chromebook or smartphone

<img src="https://github.com/trgr-karasutoragara/AI-empowers-your-mind-to-reach-anywhere/blob/main/txt-md-is-all-you-need/sample/img/Screenshot-2025-07-12%2023.06.31.png" width="400">

<br>

### Remote .txt/md AI in Action — SSH
https://youtube.com/shorts/KnFMaSmciMA?si=q-wlt3-m8a83iZaQ

<br>

## A Python demo of “.txt/md Is All You Need — A Terminal-First, AI-Powered e-Book Companion” running in an Ubuntu terminal.
https://youtu.be/Zb78wC1nqno?si=LNAH6CgHgKav10fU

<br>

## Quick Start Guide:
OCR is not supported, but a script is available to [convert .PDF files to .md format](https://github.com/trgr-karasutoragara/zen-info-your-life-is-yours/blob/main/md/pdf_to_md.py). Please use it if needed.
Install [Ollama](https://ollama.com/) and [Gemma 3 1B](https://ollama.com/library/gemma3:1b) on [Ubuntu](https://ubuntu.com/), save your [Gemini API key](https://ai.google.dev/gemini-api/docs) as an environment variable, and run the following command to start the program:

```bash
python3 reader.py your_file.txt/.md
```

You can find the script here:
[reader.py](https://github.com/trgr-karasutoragara/AI-empowers-your-mind-to-reach-anywhere/blob/main/txt-md-is-all-you-need/reader.py)


<br>

### Setting API Key as Environment Variable

#### Ubuntu (Terminal)

**Permanent (add to shell profile):**
```bash
# Add your Gemini API key to your shell profile so it's set automatically in each session
echo 'export GEMINI_API_KEY="your_actual_api_key_here"' >> ~/.bashrc

# Apply the changes immediately without restarting the terminal
source ~/.bashrc
```

#### **Additional Notes:**
- Replace `"your_actual_api_key_here"` with your real Gemini API key
- For security reasons, never commit API keys to version control
- The program will automatically detect the environment variable when started


<br>


## Philosophy & Background of Development

This project aims to contribute to developing countries and provide free and enjoyable reading experiences to the next generation—children, young people, and book lovers like you.
In developed countries, people may find it difficult to read books due to information overload. But whether you're wealthy or not, wouldn't it be fun if your Ubuntu terminal could become a reading device?

As of July 13, 2025, powerful AI still requires high-spec computers. For example, my own machine can run Gemma 3 27B, but it's quite slow. The API-based Gemini 2.0 Flash responds faster and offers more functionality.

However, technology continues to advance. One day, we may be able to read books with AI entirely offline on a local PC—asking for translations or explanations as needed. Of course, since AI can make mistakes, verification will still be necessary.

Let us remember: in the past, when cars were not yet common, physical activity was part of daily life. Today, lack of exercise has become a problem. Something similar may happen with AI.
Public domain classics are well suited for thoughtful reading.

I believe that just as torque increases when speed is reduced, slowing down enhances the power of thinking.
I hope you enjoy the experience.

<br>

## About Aozora Bunko

**Title:** *Rongo Monogatari*
**Author:** Kojin Shimomura
**Source:** Aozora Bunko (Public Domain Library)
https://www.aozora.gr.jp/cards/001097/card42923.html

This work, *Rongo Monogatari*, is a reading material written to inspire interest in the Chinese classic *The Analects of Confucius*.
In Japanese history, *The Analects* were used by the Edo Shogunate to reinforce the feudal system, so they cannot be read uncritically. However, aside from deontology and utilitarianism, *The Analects* also offer a strong philosophical foundation for considering AI ethics.
The original text is available not only in English but also in Chinese. I hope this will serve as an introduction to Eastern philosophy.

Note: Since the text is published in "JIS X 0208 / Shift\_JIS" encoding, it may not display correctly on Ubuntu systems.

To convert it to UTF-8, use the following command after downloading:

```bash
nkf -w -Lu --overwrite filename.txt
```

Aozora Bunko may help you discover authors who resonate with your sensibilities—with the help of AI.
Literature has the power to transcend time, culture, and language.
https://www.aozora.gr.jp/



<br>

## Acknowledgements
**Attention Is All You Need**

https://arxiv.org/abs/1706.03762

This project is named .txt/md Is All You Need: A Terminal-First, AI-Powered e-Book Companion out of respect and gratitude for the above paper.
I would like to express my appreciation to everyone involved in the research and development of AI.

<br>

## License
MIT License

<br>

## Author Declaration
I am an independent volunteer with no conflicts of interest.
