import re
import sys
import os

def clean_markdown_for_tts(md_text):

    # Remove everything after References/Bibliography section if it appears after the start
    lines = md_text.splitlines()
    cutoff_line = int(len(lines) * 0.2)
    heading_pattern = re.compile(r'^\s{0,3}#{1,6}\s*(References|Bibliography)\s*:?$', re.IGNORECASE)
    for i, line in enumerate(lines):
        if heading_pattern.match(line) and i > cutoff_line:
            md_text = '\n'.join(lines[:i]).rstrip()
            break
    
    # Remove markdown images
    md_text = re.sub(r'!\[[^\]]*?\]\([^\)]+?\)', '', md_text)

    # Remove HTML tables
    md_text = re.sub(r'<table[\s\S]*?</table>', '', md_text, flags=re.IGNORECASE)
    # remove markdown style tables
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

    # Join hyphenated words that were split across lines or with a space (common in PDF-to-text conversions)
    md_text = re.sub(r'(?<=\w)-( |\n)(?=\w)', lambda m: '-' if m.group(1) == ' ' else '', md_text)

    # Clean spacing
    md_text = re.sub(r'[^\S\r\n]{2,}', ' ', md_text)  # multiple spaces → one (except newlines)
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)      # multiple blank lines → 2
    md_text = md_text.strip()

    style = guess_citation_style(md_text)
    print(style) # debug
    # map each style to its removal regex or function
    removals = {
        'superscript_latex': lambda t: re.sub(r'\$\^\{[\d,\s\u2013\-–\*]+\}\$', '', t),
        'superscript_caret': lambda t: re.sub(r'\^(\d+|\*)', '', t),
        'superscript_unicode': lambda t: re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+', '', t),
        'after_period':  lambda t: re.sub(r'(?<!\d)\.(\(?\d+(?:[-–]\d+)?(?:,\d+(?:[-–]\d+)?)*\)?)\b', '', t),
        'after_comma':   lambda t: re.sub(r'(?<=\.)\(?\d+(?:[-–]\d+)?(?:,\d+(?:[-–]\d+)?)*\)?(?![\d\.])', '', t),
        'period_or_comma': lambda t: re.sub(r'(?<=[\.,])\d+(?:[-–]\d+)?(?:,\d+(?:[-–]\d+)?)*\b(?![\.\d}])', '', t),
        'numeric_bracket': lambda t: re.sub(r'\[\d+(?:[-–]\d+)?(?:,\s*\d+(?:[-–]\d+)?)*\]', '', t),
        'numeric_paren':   lambda t: re.sub(r'\(\d+(?:[-–]\d+)?(?:,\s*\d+(?:[-–]\d+)?)*\)', '', t),
        'author_date': lambda t: re.sub(r'\((?:[A-Z][a-zA-Z.\-]+(?:\s+(?:and|&)\s+[A-Z][a-zA-Z.\-]+)?(?:,\s*[A-Z][a-zA-Z.\-]+)*(?:\s+et\s+al\.)?),?\s*\d{4}[a-z]?\.?(?:\s*(?:;|,)\s*(?:[A-Z][a-zA-Z.\-]+(?:\s+(?:and|&)\s+[A-Z][a-zA-Z.\-]+)?(?:,\s*[A-Z][a-zA-Z.\-]+)*(?:\s+et\s+al\.)?),?\s*\d{4}[a-z]?\.?)*\)', '', t)
    }
    citation_remover = removals.get(style, lambda t: t)
    md_text = citation_remover(md_text)    
    
    return md_text

def guess_citation_style(md_text):
    """
    Analyze the markdown text and guess the dominant citation style.
    Returns one of:
      - 'superscript_latex'
      - 'superscript_caret'
      - 'superscript_unicode'
      - 'after_period'
      - 'after_comma'
      - 'numeric_bracket'
      - 'numeric_paren'
      - 'author_date'
      - 'period_or_comma'
      - 'undetermined'
    """
    patterns = {
        # LaTeX inline math superscripts: $^{1,2–3,*}$
        'superscript_latex': re.compile(r'\$\^\{[\d,\s\u2013\-–\*]+\}\$'),
        # Caret-based: ^1, ^*, etc.
        'superscript_caret':   re.compile(r'\^(\d+|\*)'),
        # Unicode superscript digits: ¹²³…
        'superscript_unicode': re.compile(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+'),
        # After punctuation (period) no space, no decimals
        'after_period': re.compile(r'(?<!\d)\.(\(?\d+(?:[-–]\d+)?(?:,\d+(?:[-–]\d+)?)*\)?)\b'),
        # After comma
        'after_comma':   re.compile(r'(?<=,)\d+(?:[-–]\d+)?(?:,\d+(?:[-–]\d+)?)*\b(?![\.\d}])'),
        'numeric_bracket': re.compile(r'\[\d+(?:[-–]\d+)?(?:,\s*\d+(?:[-–]\d+)?)*\]'),
        'numeric_paren':   re.compile(r'\(\d+(?:[-–]\d+)?(?:,\s*\d+(?:[-–]\d+)?)*\)'),
        'author_date': re.compile(r'\([A-Za-z].*?\d{4}[a-z]?(?:;.*?)*\)')
    }

    counts = {style: len(pat.findall(md_text)) for style, pat in patterns.items()}
    # which style has the highest count?
    best_style, best_count = max(counts.items(), key=lambda x: x[1])
    comma_count = counts['after_comma']
    
    # combine period/comma if needed
    if best_style == 'after_period' and comma_count >= 3:
        return 'period_or_comma'
    
    # require minimum matches and dominance
    others = [c for s, c in counts.items() if s != best_style]
    if best_count >= 5 and all(best_count > 1.2 * c for c in others):
        return best_style
    
    # fallback: if it’s the only non-zero style, pick it
    nonzero = [s for s,c in counts.items() if c>0]
    if len(nonzero) == 1:
        return nonzero[0]
    
    return 'undetermined'


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
        base, ext = os.path.splitext(input_file)
        output_file = base + '_tts_ready' + (ext if ext else '.md')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(clean_md)

    print("TTS-ready markdown saved as:", output_file)
