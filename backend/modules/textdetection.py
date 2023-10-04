import cv2
import numpy as np
import easyocr

readers = {
    "japanese": easyocr.Reader(["ja", "en"], gpu=True),
    # 'korean': easyocr.Reader(['ko', 'en'], gpu = True),
    # 'chinese_sim': easyocr.Reader(['ch_sim', 'en'], gpu = True),
}


def _draw_text_borders(image: np.array, borders_list: list) -> np.array:
    """ """
    if image is None or borders_list is None:
        return
    border_color = (0, 255, 0)
    border_pixel = 3

    for box, _, _ in borders_list:
        (tl, tr, br, bl) = box
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))

        cv2.rectangle(
            image, tl, br, color=border_color, thickness=border_pixel
        )

    return image


def _get_text_borders(
    image: np.array, source_lang: str = "japanese", configs: dict = {}
) -> list:
    """ """
    if image is None:
        return
    if not configs:
        return readers[source_lang].readtext(
            image, width_ths=0.7, height_ths=0.7
        )


# TODO: Check out easyocr's readtext, @fourth param for overlapping boundries
def _merge_overlapping_text_borders(list: list) -> list:
    """ """
    pass


def get_text_sections(image: np.array, source_lang: str) -> list:
    """ """
    return _get_text_borders(image, source_lang, configs={})
