# Extract Scientific Article Text from AI-Parsed PDFs

## What does this project do?

This tool takes a Markdown file generated by [MinerU](https://mineru.net/) and cleans it up to make it easier to read or feed into a text-to-speech (TTS) app.

It removes common distractions like:
- In-text citations (e.g., “[17]” or “(Smith et al., 2020)”)
- Broken line breaks, hyphenated words, and irregular spacing
- The References section and anything that comes after it (if detected)

The result isn’t perfect—there may still be some extra material before or after the main article—but it makes the main sections (Introduction, Methods, etc.) much easier to spot and copy into a TTS app or other reader.

---

## Requirements

* `pylatexenc` library:

  ```bash
  pip install pylatexenc
  ```

* A `.md` file from your scientific article.
  You can convert the PDF yourself, or use [MinerU](https://mineru.net/) (or [MinerU 2.0](https://mineru.net/OpenSourceTools/Extractor), registration required).

---

## Input and Output

**Input:**  
- A `.md` file produced by MinerU, containing text extracted from a scientific article PDF

**Output:**  
- A cleaned `.txt` or `.md` file with:
  - Fewer formatting issues
  - No in-text citation clutter
  - Better flow for reading or listening

---

## Usage

```bash
python edit_pdf_converter_output.py input.md [output.md]
```
* If `output.md` is not given, the script creates `input_tts_ready.md`.

*Example:*

```bash
python edit_pdf_converter_output.py parsed.md cleaned.md
```

---

## Implementation

- Detects and removes the most common citation style in the file (author-date or numbered)
- Removes mid-word hyphens, extra newlines, and double spaces
- Cuts off the file at the start of the References section
- Outputs the cleaned result to a new file

---

## Why this project?

Copying text from scientific PDFs—especially AI-parsed ones—often results in messy formatting and citation overload. This tool helps clean things up so the important content is easier to read, listen to, or reuse.

---

_This project was done as part of the [Basic programming skills (Python)](https://github.com/Code-Maven/wis-python-course-2025-03) course._

_The writing of this README.md file was ordered by me and outputted by ChatGPT, as was much of the code._
