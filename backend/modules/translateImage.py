from googletrans import Translator
import pytesseract
import numpy

SUPPORTED_LANG = {
    "english": "en",
    "japanese": "ja",
    "korean": "ko",
}

translator = Translator()


def translate_to_destination_lang(untranslated: str, source_lang: str) -> str:
    """ """
    if isinstance(untranslated, str):
        if source_lang == "japanese":
            return _translate_japanese_string_to_dest_string(untranslated)


# ============================================================================
"""
Below contains @hidden methods
"""


# TODO
# - Work on error handling in case translation to destLang fails
def _translate_japanese_string_to_dest_string(
    japaneseString: str, destLang: str = "english"
) -> str:
    """
    Parameters
    ----------
    japaneseString : str
        the japanese string to transate to destLang
    destLang : str, optional
        the language we wish to translate japaneseString to (default is 'english')

    Returns
    ----------
    string
        Translated string to destLang language
    """

    jpGoogleTrnsCode = SUPPORTED_LANG["japanese"]
    destGoogleTrnsCode = SUPPORTED_LANG[destLang]

    if japaneseString.strip() == "":
        return ""

    translatedEnglishStr = translator.translate(
        japaneseString, src=jpGoogleTrnsCode, dest=destGoogleTrnsCode
    )
    return translatedEnglishStr.text


# ============================================================================
"""
Below contains @deprecated methods
"""


def _generate_pytesseract_config(sourceLang: str) -> str:
    """
    @deprecated
    """
    return r"--oem 3 --psm 5 -l jpn_vert"


# assume that the image only constains text and NO other backgrounds
def _translate_image_to_string(image, sourceLang: str):
    """
    @deprecated
    """
    pytesseract_config = r"--oem 3 --psm 5 -l jpn_vert"

    # Add error handling here if required
    textContents = pytesseract.image_to_string(image, pytesseract_config)

    return textContents
