def flatten_text(text):
    '''Function to flatten the text in a single line'''
    flattened_text = text.replace('\n', ' ')
    flattened_text = ' '.join(flattened_text.split())
    return flattened_text

def insert_line_breaks(text, limit=130):
    '''Function to insert line breaks'''
    lines = []
    while len(text) > limit:
        breakpoint = text.rfind(' ', 0, limit)
        if breakpoint == -1:  # No space found, force break
            breakpoint = limit
        lines.append(text[:breakpoint])
        text = text[breakpoint:].lstrip()  # Remove leading spaces from the remaining text
    lines.append(text)
    return '\n'.join(lines)

def format_text_with_line_breaks(text, limit=130):
    '''Function to separate the paragraphs before inserting line breaks'''
    paragraphs = text.split('\n\n')
    formatted_paragraphs = [insert_line_breaks(paragraph, limit) for paragraph in paragraphs]
    return '\n\n'.join(formatted_paragraphs)