import re
import sys

def clean_markdown_for_tts(md_text):
    # 1. Remove in-text references (superscript style, bracketed numbers, parenthetical references)
    md_text = re.sub(r'(?<=\w)\s*\^?\d+\b', '', md_text)  # e.g., text^1 or text 1
    md_text = re.sub(r'\[(\d+([-,]\s?\d+)*|(\d+,?\s?)+)\]', '', md_text)
    md_text = re.sub(r'\((?:[A-Z][a-zA-Z]+(?:,? (?:&|and) [A-Z][a-zA-Z]+)*,? (?:et al\.,? )?\d{4}(?:; ?[A-Z][a-zA-Z]+,? \d{4})*)\)', '', md_text)
    md_text = re.sub(r'\s{2,}', ' ', md_text)

    # 2. Remove figure/table references (e.g., (Figure 1c), [Table 2], etc.)
    md_text = re.sub(r'\(?(Figure|Fig\.?|Table|Tab\.?)\s*\d+[a-zA-Z]?\)?', '', md_text, flags=re.IGNORECASE)
    md_text = re.sub(r'\[?(Figure|Fig\.?|Table|Tab\.?)\s*\d+[a-zA-Z]?\]?', '', md_text, flags=re.IGNORECASE)

    # 3. Remove images (markdown: ![alt](url))
    md_text = re.sub(r'!\[.*?\]\(.*?\)', '', md_text)

    # 4. Remove tables (markdown tables: lines with | and ---)
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

    # 5. Remove extra spaces after hyphens (e.g., "well- known" -> "well-known")
    md_text = re.sub(r'-\s+', '-', md_text)

    # 6. Remove leftover multiple blank lines
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)

    # 7. Remove References/Bibliography section if it appears after the start
    # Look for headings like 'References', 'Bibliography', possibly with markdown heading symbols
    pattern = re.compile(r'^(#{0,3}\s*(References|Bibliography)\s*)$', re.IGNORECASE | re.MULTILINE)
    matches = list(pattern.finditer(md_text))
    if matches:
        # Only remove if the heading is after the first 20% of the file
        cutoff = int(len(md_text) * 0.2)
        for match in matches:
            if match.start() > cutoff:
                md_text = md_text[:match.start()].rstrip()
                break  # Remove only from the first such heading after the cutoff

    # 8. Strip leading/trailing whitespace
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
