import re
import sys

def clean_markdown_for_tts(md_text):
    # print(repr(md_text[:500]))  # Debug: print first 500 characters of the input markdown
    
    # 1. Remove References/Bibliography section if it appears after the start
    # Look for headings like 'References', 'Bibliography', possibly with markdown heading symbols
    lines = md_text.splitlines()
    cutoff_line = int(len(lines) * 0.2)
    heading_pattern = re.compile(r'^\s{0,3}#{0,6}\s*(References|Bibliography)\s*:?$', re.IGNORECASE)
    for i, line in enumerate(lines):
        if heading_pattern.match(line):
            if i > cutoff_line:
                md_text = '\n'.join(lines[:i]).rstrip()
                break
    
    # 2. Remove numeric citations after punctuation, like ".40,42–44" or ").12,13"
    md_text = re.sub(r'(?<=[\.\)])\s*\d+(?:[,\u2013-]\s*\d+)*', '', md_text)

    # 3. Remove parenthetical or bracketed figure/table refs only
    md_text = re.sub(
        r'[\(\[]\s*(?:see\s+)?(?:Figure|Fig\.?|Table|Tab\.?)\s*S?\d+[a-zA-Z]?(?:[,\u2013\-–]\s*\d+[a-zA-Z]?)?\s*[\)\]]',
        '',
        md_text,
        flags=re.IGNORECASE
    )
    
    # 2. Remove in-text references (superscript style, bracketed numbers, parenthetical references)
    md_text = re.sub(r'(?<=\w)\s*\^?\d+\b', '', md_text)  # e.g., text^1 or text 1
    md_text = re.sub(r'\[(\d+([-,]\s?\d+)*|(\d+,?\s?)+)\]', '', md_text) # e.g., [1], [1, 2], [1-3]
    md_text = re.sub(r'\((?:[A-Z][a-zA-Z]+(?:,? (?:&|and) [A-Z][a-zA-Z]+)*,? (?:et al\.,? )?\d{4}(?:; ?[A-Z][a-zA-Z]+,? \d{4})*)\)', '', md_text) # e.g., (Smith et al., 2020), (Smith, 2020; Johnson, 2019)
    md_text = re.sub(r'[^\S\r\n]{2,}', ' ', md_text)  # Replace only multiple spaces, not newlines

    


    # 4. Remove images (markdown: ![alt](url))
    md_text = re.sub(r'!\[.*?\]\(.*?\)', '', md_text) # e.g., ![image](image_url)

    # 5. Remove tables (markdown tables: lines with | and ---)
    lines = md_text.split('\n')
    cleaned_lines = []
    in_table = False
    for line in lines:
        if re.match(r'^\s*\|.*\|\s*$', line) or re.match(r'^\s*\|?(\s*:?-+:?\s*\|)+\s*$', line): # Match table rows or header separators
            in_table = True
            continue
        if in_table and not line.strip(): # If we were in a table and hit an empty line, exit table mode
            in_table = False
            continue
        if not in_table: # Only keep lines that are not part of a table
            cleaned_lines.append(line)
    md_text = '\n'.join(cleaned_lines)

    # 6. Remove extra spaces after hyphens (e.g., "well- known" -> "well-known")
    md_text = re.sub(r'-\s+', '-', md_text)

    # 7. Remove leftover multiple blank lines
    md_text = re.sub(r'\n{3,}', '\n\n', md_text) # Replace three or more newlines with two

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
