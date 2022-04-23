
def get_text_in_brackets(text, symbol_start, symbol_end):
    """Function to get contents between 2 symbols.
    :param text:            Given Text
    :param symbol_start:
    :param symbol_end:
    :return:
    e.g.
    get_text_in_brackets('This is [not] important message', '[', ']')
    => 'not'"""
    start = text.find(symbol_start) + len(symbol_start) if symbol_start in text else None
    stop = text.find(symbol_end) if symbol_end in text else None
    return str(text[start:stop])
