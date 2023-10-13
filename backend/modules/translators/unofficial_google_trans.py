"""
This module, unofficial_google_trans, contains the unofficial google translate
API. It is mostly used for testing purposes since the translator itself is not
very good and has many limitations. Do NOT use this as the official translator

TODO:
    Add supports for multiple other languages

"""

from googletrans import Translator
import httpx

SUPPORTED_LANG = {
    "english": "en",
    "japanese": "ja",
    "korean": "ko",
}

max_timeout = httpx.Timeout(5)
translator = Translator(timeout=max_timeout)


# TODO: Needs to support at least Korean and Mandarin as well.
# TODO: We don't want to limit destination translation to english, but other
# languages as well. Add another parameter, dest_lang: str
# TODO: We want to slowly add support for multiple languages, not just 
# english, mandarin, korean and japanese.
def translate_to_destination_lang(untranslated: str, source_lang: str) -> str:
    """
    Translate the provided string into English given the source lang of the str

    Parameters
    ----------
    untranslated : str
        The untranslated string to translate

    source_lang : str
        The source language of the untranslated string

    Returns
    -------
    str
        The translated string in english

    """
    if isinstance(untranslated, str):
        if source_lang == "japanese":
            return translate_japanese_string_to_dest_string(untranslated)


# TODO Work on error handling in case translation to destLang fails
# TODO Work on the case when the provided string is empty
def translate_japanese_string_to_dest_string(
    japanese_string: str, dest_lang: str = "english"
) -> str:
    """
    Parameters
    ----------
    japanese_string : str
        the japanese string to transate to destLang
    dest_lang : str, optional
        the language we wish to translate japaneseString to destLang

    Returns
    ----------
    string
        Translated string to destLang language

    """

    jp_Google_Trns_Code = SUPPORTED_LANG["japanese"]
    dest_Google_Trns_Code = SUPPORTED_LANG[dest_lang]

    if japanese_string.strip() == "":
        return ""

    translatedEnglishStr = translator.translate(
        japanese_string, src=jp_Google_Trns_Code, dest=dest_Google_Trns_Code
    )
    return translatedEnglishStr.text


# TODO: Implement the function
def translate_korean_string_to_dest_string(
    korean_string: str, dest_lang: str = "english"
) -> str:
    """"""
    pass


# TODO: Implement the function
def translate_mandarin_string_to_dest_string(
    mandarin_string: str, dest_lang: str = "english"
) -> str:
    """"""
    pass