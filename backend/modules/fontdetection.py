import math
import textwrap
from PIL import ImageFont

DEFAULT_FONT_NAME = "wild-words"
DEFAULT_FONT_PATH = "utilities/fonts/Wild-Words-Roman.ttf"
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_COLOR = "#000"
MINIMUM_FONT_SIZE = 10
MAXIMUM_FONT_SIZE = 72
MIN_IMG_SPACE_THRESHOLD = 5

def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return [text_width, text_height]

def calculate_font_size (src_text, start_pos, end_pos, font_name=DEFAULT_FONT_NAME, font_color=DEFAULT_FONT_COLOR, font_thickness=1):
    """"""
    image_width = abs(end_pos[0] - start_pos[0])
    image_height = abs(end_pos[1] - start_pos[1])

    # line_height_gap = interpolate()
    line_height_gap = 2
    line_width_gap = 2
    padding = 3

    font_size = DEFAULT_FONT_SIZE
    font_path = DEFAULT_FONT_PATH

    if font_name == "wild-words":
        font_path = "utilities/fonts/Wild-Words-Roman.ttf"
    
    left = MINIMUM_FONT_SIZE
    right = MAXIMUM_FONT_SIZE

    def calc_total_text_height (size) -> int:
        font_type = ImageFont.truetype(font_path, size)
        text_width, text_height = get_text_dimensions(src_text,  font_type)
        text_width = math.floor((image_width - padding * 2) / text_width)
        if text_width <= 0:
            return -1

        content = textwrap.wrap(
            src_text, width=text_width, break_long_words=False
        )
        num_of_lines = len(content)
        total_height = num_of_lines * text_height + (padding * 2)
        return total_height

    def is_font_size_small (curr_font_size: int) -> bool:
        total_height = calc_total_text_height(curr_font_size)

        if image_height >= total_height and image_height <= total_height + MIN_IMG_SPACE_THRESHOLD:
            return False
        elif total_height == -1:
            return False
        else:
            return True

    def is_font_size_big (curr_font_size: int) -> bool:
        total_height = calc_total_text_height(curr_font_size)

        if total_height == -1:
            return True

        return total_height >= image_height


    while left <= right:
        mid_font_size = math.floor((left + right) / 2)
        if is_font_size_small(mid_font_size):
            left = mid_font_size + 1
        elif is_font_size_big(mid_font_size):
            right = mid_font_size - 1
        else:
            return mid_font_size
        
    # return min_in_range(mid_font_size) # ex if font sz = 14 and [12, 13, 14, 15] = [12], we return 12 font size
    print('final size is ', mid_font_size)
    print('[============================DONE===============================]')
    return mid_font_size
