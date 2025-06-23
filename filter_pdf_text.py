import fitz  # PyMuPDF

header_font = ''


def extract_text_and_styles(pdf_path, reg_txt_size, reg_txt_font):
    doc = fitz.open(pdf_path)
    all_text = ""
    reg_txt_flags = 4 # flag for for nnonstylized text

    for page_num, page in enumerate(doc, start=1):
        # if page_num > 3: return  # Limit to first 10 pages for performance
        print(f"\n--- Page {page_num} ---")
        # continue
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                    if 'components' in text:
                        print('components')
                        pass

                    font = span.get("font", "Unknown")
                    size = span.get("size", "N/A")
                    flags = span.get("flags", 0)
                    color = "#{:06x}".format(span["color"])  # RGB hex
                    bold = "Bold" if "Bold" in font else "Regular"
                    italic = "Italic" if "Italic" in font else "Normal"

                    print(f'"{text}" | Font: {font}, Size: {size}, Style: {bold}, {italic}, Color: {color}')

                    # Accumulate text for further processing if needed
                    if font == reg_txt_font and size == reg_txt_size and flags == reg_txt_flags:
                        all_text += f"{text} "
    # save the extracted text to a file
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(all_text)

def pre_analyze_pdf(pdf_path):
    # read the first 3 pages of pdf and return the most prevalent font size and font name
    doc = fitz.open(pdf_path)   
    font_sizes = {}
    font_names = {}
    reg_txt_size = 0
    reg_flag = 0            
    for page_num, page in enumerate(doc, start=1):
        if page_num > 3: break  # Limit to first 3 pages for performance
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = span.get("size", 0)
                    font = span.get("font", "Unknown")
                    flags = span.get("flags", 0)

                    # Count font sizes
                    if size not in font_sizes:
                        font_sizes[size] = 0
                    font_sizes[size] += 1

                    # Count font names
                    if font not in font_names:
                        font_names[font] = 0
                    font_names[font] += 1

                   
    # Find the most prevalent font size and name
    most_prevalent_size = max(font_sizes, key=font_sizes.get, default= 0)
    most_prevalent_font = max(font_names, key=font_names.get, default="Unknown")
    print(f"Most prevalent font size: {most_prevalent_size}")
    print(f"Most prevalent font name: {most_prevalent_font}")
    return most_prevalent_size, most_prevalent_font 


if __name__ == "__main__":
    # Example usage:
    reg_txt_size, reg_txt_font = pre_analyze_pdf("example.pdf")
    extract_text_and_styles("example.pdf", reg_txt_size, reg_txt_font)
