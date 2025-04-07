

def determine_section_name_at_offset(markdown:str, offset:int) -> str:
    ## Find the nearest heading before the offset
    ## Find the nearest heading after the offset
    ## Return the heading with the smallest distance
    h1_name = None
    h2_name = None
    h3_name = None
    h4_name = None
    arr = markdown.split("\n")
    counter = 0
    for idx, line in enumerate(arr):
        if line.startswith("# "):
            h1_name = line[2:].strip()
        elif line.startswith("## "):
            h2_name = line[3:].strip()
        elif line.startswith("### "):
            h3_name = line[4:].strip()
        elif line.startswith("#### "):
            h4_name = line[5:].strip()
        counter += len(line)
        if counter >= offset: break

    section_name = ""
    if h1_name is not None: section_name = h1_name
    if h2_name is not None:
        if len(section_name) == 0: section_name = h2_name
        else: section_name = f"{section_name} / {h2_name}"
    if h3_name is not None:
        if len(section_name) == 0: section_name = h3_name
        else: section_name = f"{section_name} / {h3_name}"
    if h4_name is not None:
        if len(section_name) == 0: section_name = h4_name
        else: section_name = f"{section_name} / {h4_name}"
    return section_name

def find_prior_context(markdown:str, offset:int) -> str:
    # Look back from the offset to find the last 2 paragraphs of text
    
    ## Start by looking for the previous word
    prev_space = markdown.rfind(" ", 0, offset)
    if prev_space == -1: return ""

    ## Then find the previous newline
    prev_newline = markdown.rfind("\n", 0, prev_space)
    if prev_newline == -1: return ""

    ## Then find the previous newline before that
    prev_newline2 = markdown.rfind("\n", 0, prev_newline)
    if prev_newline2 == -1: 
        return markdown[prev_newline:offset].strip()
    else:
        return markdown[prev_newline2:offset].strip()


def find_post_context(markdown:str, offset:int) -> str:
    # Look forward from the offset to find the next 2 paragraphs of text
    
    # Start by looking for the next word
    next_space = markdown.find(" ", offset)

    ## Start by looking for the next newline
    next_newline = markdown.find("\n", next_space)
    if next_newline == -1: return ""

    ## Then find the next newline after that
    next_newline2 = markdown.find("\n", next_newline+1)
    if next_newline2 == -1: 
        return markdown[offset:next_newline].strip()
    else:
        return markdown[offset:next_newline2].strip()

    

