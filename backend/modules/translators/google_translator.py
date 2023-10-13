"""
This module, google_translator, contains the Google Translate API functions
used to translate the texts into english language. All credentials must be 
exported out from this page for security reasons. 

"""
from google.cloud import translate_v2 as translate


def translate_text(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print(
        "Detected source language: {}".format(result["detectedSourceLanguage"])
    )

    return result
