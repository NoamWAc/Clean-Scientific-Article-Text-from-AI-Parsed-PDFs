import re
import sys

import re

def clean_markdown_for_tts(md_text):
    # 0. Remove author and correspondence blocks (look near the top)
    md_text = re.sub(r'(?s)^.*?(correspondence|author information|authors?[\s:]).*?\n\n', '', md_text, flags=re.IGNORECASE)

    # 1. Remove References/Bibliography section if it appears after the start
    lines = md_text.splitlines()
    cutoff_line = int(len(lines) * 0.2)
    heading_pattern = re.compile(r'^\s{0,3}#{0,6}\s*(References|Bibliography)\s*:?$', re.IGNORECASE)
    for i, line in enumerate(lines):
        if heading_pattern.match(line) and i > cutoff_line:
            md_text = '\n'.join(lines[:i]).rstrip()
            break

    # 2. Remove numeric citations like ".40,42–44" or ").12"
    md_text = re.sub(r'(?<=[\.\)])\s*\d+(?:[,\u2013\-–]\s*\d+)*', '', md_text)

    # 3. Remove LaTeX-style superscript references like $^{1,7}$ or $^{22–25}$
    md_text = re.sub(r'\$\^\{[\d,\s\u2013\-–\*]+\}\$', '', md_text)  # $^{1,2–4,*}$

    # 4. Remove other superscript-style references: ^1 or Unicode superscripts
    md_text = re.sub(r'\^(\d+|[*])', '', md_text)           # ^1 or ^*
    md_text = re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+', '', md_text)         # Unicode superscripts

    # 5. Remove parenthetical/bracketed figure/table references
    md_text = re.sub(
    r'\s?[\(\[]\s*(?:see\s+)?(?:(?:Figure|Fig\.?|Table|Tab\.?)\s*S?\d+[a-zA-Z]?'
    r'(?:[,\-–\u2013]\s*S?\d+[a-zA-Z]?)*'
    r'|\s*(?:and|or)\s*'
    r'(?:Figure|Fig\.?|Table|Tab\.?)\s*S?\d+[a-zA-Z]?)*\s*[\)\]]',
    '',
    md_text,
    flags=re.IGNORECASE
    )
    

    # 6. Remove images
    md_text = re.sub(r'!\[.*?\]\(.*?\)', '', md_text)

    # 7. Remove tables
    lines = md_text.split('\n')
    cleaned_lines = []
    in_table = False
    for line in lines:
        if re.match(r'^\s*\|.*\|\s*$', line) or re.match(r'^\s*\|?(\s*:?-+:?\s*\|)+\s*$', line):
            in_table = True
            continue
        if in_table and not line.strip():
            in_table = False
            continue
        if not in_table:
            cleaned_lines.append(line)
    md_text = '\n'.join(cleaned_lines)

    # 8. Fix hyphens and spacing (but keep math intact)
    # ⚠️ Don't remove spaces in LaTeX math like $\sim 1$
    def preserve_math(m):
        content = m.group(0)
        return re.sub(r'-\s+', '-', content)

    md_text = re.sub(r'\$.*?\$', preserve_math, md_text)  # Fix spacing in math blocks
    md_text = re.sub(r'-\s+', '-', md_text)               # Elsewhere: fix "well- known" → "well-known"

    # 9. Clean spacing
    md_text = re.sub(r'[^\S\r\n]{2,}', ' ', md_text)  # multiple spaces → one (except newlines)
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)      # multiple blank lines → 2
    md_text = md_text.strip()

    return md_text


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python edit_pdf_converter_output.py <input_markdown_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_md = f.read()

    clean_md = clean_markdown_for_tts(raw_md)

    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = input_file.replace('.md', '_tts_ready.md')
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(clean_md)

    print("TTS-ready markdown saved as:", output_file)
