import re
import unicodedata
from typing import Optional
from bs4 import BeautifulSoup


def remove_html_tags(text: str) -> str:
    """
    Remove html tags from text like <br/> , etc. You can use BeautifulSoup for this.

    Args:
        text : str
            Input string.

    Return:
        str
            Output string.
    """
    # TODO
    soup = BeautifulSoup(text, 'html.parser')
    text_result = soup.get_text()
    return text_result

def remove_accented_chars(text: str) -> str:
    """
    Remove accents from input string.

    Args:
        text : str
            Input string.

    Return:
        str
            Output string.
    """
    # TODO
    no_accented_text  = ''.join(char for char in unicodedata.normalize('NFD', text)
                   if unicodedata.category(char) != 'Mn')
    
    return no_accented_text

def remove_special_chars(text: str, remove_digits: Optional[bool] = False) -> str:
    """
    Remove non-alphanumeric characters from input string.

    Args:
        text : str
            Input string.
        remove_digits : bool
            Remove digits.

    Return:
        str
            Output string.
    """
    # TODO
    regex = ""
    if not remove_digits:
        regex = r'[^a-zA-Z0-9\s,.;:]'
    else :
        regex = r'[^a-zA-Z\s,.;:]'
    
    text_removed_chars = re.sub(regex, '', text)

    return text_removed_chars


def remove_extra_new_lines(text: str) -> str:
    """
    Remove extra new lines or tab from input string.

    Args:
        text : str
            Input string.

    Return:
        str
            Output string.
    """
    # TODO
    textReplaced = text.replace("\t", " ").replace("\n", " ")
    return textReplaced


def remove_extra_whitespace(text: str) -> str:
    """
    Remove any whitespace from input string.

    Args:
        text : str
            Input string.

    Return:
        str
            Output string.
    """
    # TODO
    result_test = re.sub(r'\s+', ' ', text)
    return result_test

def clean_func(
    text: str
) -> str:
    """
    Normalize list of strings (corpus)

    Args:
        text : str : InputText to be converted
        
    Return:
        str
            Normalized text.
    """

    cleaned_text = text 
    cleaned_text = remove_html_tags(cleaned_text)
    cleaned_text = remove_accented_chars(cleaned_text)
    cleaned_text = remove_special_chars(cleaned_text)
    cleaned_text = remove_extra_new_lines(cleaned_text)
    cleaned_text = remove_extra_whitespace(cleaned_text)

    return cleaned_text