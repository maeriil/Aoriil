from googletrans import Translator
import pytesseract
import numpy

SUPPORTED_LANG = {
    "english": "en",
    "japanese": "ja",
    "korean": "ko",
}

translator = Translator()

# TODO make this more general so it supports multiple lang
def generatePytesseractConfig(sourceLang: str) -> str:
    return r"--oem 3 --psm 5 -l jpn_vert"

# TODO this will call the text extractor module
def extractTextFromImage (image):
    # do something here
    return ""


# assume that the image only constains text and NO other backgrounds
def translateImageToString (image, sourceLang: str):
    pytesseract_config = r"--oem 3 --psm 5 -l jpn_vert"

    # Add error handling here if required
    textContents = pytesseract.image_to_string(image, pytesseract_config)

    return textContents


# TODO
# - Work on error handling in case translation to destLang fails
def translateJapaneseStringToDestString(japaneseString: str, destLang: str = 'english') -> str:
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

    translatedEnglishStr = translator.translate(
        japaneseString, src=jpGoogleTrnsCode, dest=destGoogleTrnsCode
    )

    return translatedEnglishStr.text
