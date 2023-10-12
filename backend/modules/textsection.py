import utilities.helpers.imageHelpers as imgutil

import cv2
import math
import numpy as np

MAX_EDGE_THRESHOLD = 0.5


class textsection:
    """"""

    def __init__(
        self, text, position, font_size, font_type="placeholder"
    ) -> None:
        self.set_text(text)
        self.set_font_size(font_size)
        self.set_font_type(font_type)
        self.set_position(position)

    def set_text(self, text: str) -> None:
        self.text = text

    def set_font_size(self, font_size: int) -> None:
        self.font_size = font_size

    def set_font_type(self, font_type: int) -> None:
        self.font_type = font_type

    def set_position(self, position: list) -> None:
        (x_min, x_max, y_min, y_max) = map(math.floor, position)

        self.start_pos = [x_min, y_min]
        self.end_pos = [x_max, y_max]
        self.width = x_max - x_min
        self.height = y_max - y_min

    def __str__(self) -> str:
        return f"[text={self.text}, start=[{self.start_pos[0]},{self.start_pos[1]}], end=[{self.end_pos[0]},{self.end_pos[1]}], width={self.width}, height={self.height}, font-sz={self.font_size}, font-type={self.font_type}]\n\n"


class parenttextsection:
    """"""

    def __init__(self, section: textsection) -> None:
        self.text = section.text

        self.orig_width = section.width
        self.orig_height = section.height
        self.orig_start_pos = section.start_pos
        self.orig_end_pos = section.end_pos

        self.width = section.width
        self.height = section.height
        self.start_pos = section.start_pos
        self.end_pos = section.end_pos

        self.font_size = section.font_size
        self.font_type = section.font_type

        self.children = []

    def __str__(self) -> str:
        content = "[\n"

        top = f"    Parent = [text={self.text}, start=[{self.start_pos[0]},{self.start_pos[1]}], end=[{self.end_pos[0]},{self.end_pos[1]}], width={self.width}, height={self.height}, font-sz={self.font_size}, font-type={self.font_type}]\n"
        self_val = f"   Original = [text={self.text}, start=[{self.orig_start_pos[0]},{self.orig_start_pos[1]}], end=[{self.orig_end_pos[0]},{self.orig_end_pos[1]}], width={self.orig_width}, height={self.orig_height}, font-sz={self.font_size}, font-type={self.font_type}]"
        children = "\nchildren=[\n"

        for child in self.children:
            children += child.__str__() + "\n"
        children += "\n]\n"

        return content + top + self_val + children + "\n]\n\n"

    def add_section(self, section: textsection) -> None:
        """"""
        self.children.append(section)

        x_min_section, y_min_section = section.start_pos
        x_max_section, y_max_section = section.end_pos

        x_min_self, y_min_self = self.start_pos
        x_max_self, y_max_self = self.end_pos

        x_min_merge = min(x_min_section, x_min_self)
        y_min_merge = min(y_min_section, y_min_self)
        x_max_merge = max(x_max_section, x_max_self)
        y_max_merge = max(y_max_section, y_max_self)

        self.start_pos = [x_min_merge, y_min_merge]
        self.end_pos = [x_max_merge, y_max_merge]
        self.width = abs(x_max_merge - x_min_merge)
        self.height = abs(y_max_merge - y_min_merge)

    def similar_fonts(self, section: textsection) -> bool:
        return section.font_size in range(
            self.font_size - 5, self.font_size + 5
        )

    def overlaps(self, section: textsection) -> bool:
        """
        TODO: Change the way overlaps function works. Right now, it takes in
                two rectangular boxes and determines if corners lies inside
                the boxes, instead check for overlaps using start_x, start_y
                end_x, end_y only.
        """
        section1 = generate_box(self.start_pos, self.end_pos)
        section2 = generate_box(section.start_pos, section.end_pos)

        return is_section_overlap(section1, section2)

    def is_merging_too_big(
        self, section: textsection, image: np.array
    ) -> bool:
        """"""
        mstart, mend = merge_dimensions(
            self.start_pos, self.end_pos, section.start_pos, section.end_pos
        )
        mwidth = abs(mend[0] - mstart[0])
        mheight = abs(mend[1] - mstart[1])

        print("width is ", mwidth)
        print("height is ", mheight)

        imgheight, imgwidth, channel = image.shape

        print("img width ", imgwidth)
        print("img height ", imgheight)
        widthratio = mwidth / imgwidth
        heightratio = mheight / imgheight

        if widthratio > 0.5 or heightratio > 0.5:
            return True
        return False

    def draw_section(self, image: np.array) -> np.array:
        """"""
        border_color = (0, 255, 0)
        border_pixel = 1

        cv2.rectangle(
            image,
            self.start_pos,
            self.end_pos,
            color=border_color,
            thickness=border_pixel,
        )
        return image

    def completely_above(self, section: textsection) -> bool:
        """"""
        # self section is completely above if self's end_y > section's start_y
        return self.end_pos[1] < section.start_pos[1]

    def completely_below(self, section: textsection) -> bool:
        """"""
        # self section is completely above if self's start_y < section's end_y
        return self.start_pos[1] > section.end_pos[1]

    def in_y_axis_range(self, section: textsection) -> bool:
        """"""
        # a section is in yaxis range with section if its neither completely
        # above nor completely below
        return not self.completely_above(
            section
        ) and not self.completely_below(section)

    def completely_left(self, section: textsection) -> bool:
        """"""
        # self section is completely left if self's end_x < section's start_x
        return self.end_pos[0] < section.start_pos[0]

    def completely_right(self, section: textsection) -> bool:
        """"""
        # self section is completely left if self's start_x > section's end_x
        return self.start_pos[0] > section.end_pos[0]

    def y_difference(self, section: textsection) -> int:
        above_diff = abs(self.end_pos[1] - section.start_pos[1])
        below_diff = abs(section.end_pos[1] - self.start_pos[1])

        return min(above_diff, below_diff)

    def in_x_axis_range(self, section: textsection) -> bool:
        """"""
        # a section is in xaxis range with section if its neither left
        # above nor completely right
        return not self.completely_left(section) and not self.completely_right(
            section
        )

    def x_difference(self, section: textsection) -> int:
        right_diff = abs(self.end_pos[0] - section.start_pos[0])
        left_diff = abs(section.end_pos[0] - self.start_pos[0])

        return min(left_diff, right_diff)

    def contains_edges_yaxis(
        self, section: textsection, image: np.array
    ) -> bool:
        """"""
        start_pos_x = min(self.start_pos[0], section.start_pos[0])
        end_pos_x = max(self.end_pos[0], section.end_pos[0])
        start_pos_y = 0
        end_pos_y = 0

        is_above = self.completely_above(section)
        is_below = self.completely_below(section)

        if is_above:
            start_pos_y = self.end_pos[1]
            end_pos_y = section.start_pos[1]
        elif is_below:
            start_pos_y = section.end_pos[1]
            end_pos_y = self.start_pos[1]

        cropped_img = imgutil.crop_image(
            image, [start_pos_x, start_pos_y], [end_pos_x, end_pos_y]
        )
        width = abs(end_pos_x - start_pos_x)
        height = abs(end_pos_y - start_pos_y)
        if height <= 0 or width <= 0:
            return False
        longest_edge = calculate_long_edge(cropped_img)

        return (longest_edge / height) >= MAX_EDGE_THRESHOLD

    def contains_edges_xaxis(
        self, section: textsection, image: np.array
    ) -> bool:
        """"""
        start_pos_x = 0
        end_pos_x = 0
        start_pos_y = min(self.start_pos[1], section.start_pos[1])
        end_pos_y = max(self.end_pos[1], section.end_pos[1])

        is_left = self.completely_left(section)

        if is_left:
            start_pos_x = self.end_pos[0]
            end_pos_x = section.start_pos[0]
        else:
            start_pos_x = section.end_pos[0]
            end_pos_x = self.start_pos[0]

        cropped_img = imgutil.crop_image(
            image, [start_pos_x, start_pos_y], [end_pos_x, end_pos_y]
        )
        width = abs(end_pos_x - start_pos_x)
        height = abs(end_pos_y - start_pos_y)
        if height <= 0 or width <= 0:
            return False

        longest_edge = calculate_long_edge(cropped_img)

        return (longest_edge / width) >= MAX_EDGE_THRESHOLD


def merge_dimensions(start_pos1, end_pos1, start_pos2, end_pos2):
    mstart_x = min(start_pos1[0], start_pos2[0])
    mstart_y = min(start_pos1[1], start_pos2[1])
    mend_x = max(end_pos1[0], end_pos2[0])
    mend_y = max(end_pos1[1], end_pos2[1])

    return [mstart_x, mstart_y], [mend_x, mend_y]


def is_section_overlap(section1: list, section2: list) -> bool:
    section1_tl, section1_tr, section1_br, section1_bl = imgutil.unpack_box(
        section1
    )

    is_inside_section2 = (
        is_point_in_rectangle(section1_tl, section2)
        or is_point_in_rectangle(section1_tr, section2)
        or is_point_in_rectangle(section1_br, section2)
        or is_point_in_rectangle(section1_bl, section2)
    )
    if is_inside_section2:
        return True

    section2_tl, section2_tr, section2_br, section2_bl = imgutil.unpack_box(
        section2
    )

    # Case1.2: There exists point inside section1's rectangle.
    is_inside_section1 = (
        is_point_in_rectangle(section2_tl, section1)
        or is_point_in_rectangle(section2_tr, section1)
        or is_point_in_rectangle(section2_br, section1)
        or is_point_in_rectangle(section2_bl, section1)
    )
    if is_inside_section1:
        return True

    # These two rectangles then dont overlap
    return False


def is_point_in_rectangle(point: list, rectangle: list) -> bool:
    (tl, tr, br, bl) = imgutil.unpack_box(rectangle)
    x1, y1, x2, y2 = tl[0], tl[1], br[0], br[1]
    x, y = point[0], point[1]

    if (x1 <= x and x <= x2) and (y1 <= y and y <= y2):
        return True
    return False


def generate_box(start_pos: list, end_pos: list) -> list:
    start_x, start_y = start_pos[0], start_pos[1]
    end_x, end_y = end_pos[0], end_pos[1]

    return [start_pos, [end_x, start_y], end_pos, [start_x, end_y]]


def should_merge_sections(
    parent_section: parenttextsection,
    child_section: textsection,
    MAXIMUM_GAP_DIST: int,
    image: np.array,
) -> bool:
    """ """
    if parent_section.is_merging_too_big(child_section, image):
        print("merging is too big???")
        return False
    if parent_section.overlaps(child_section):
        print("overlaps so we merge it")
        return True
    elif parent_section.y_difference(child_section) < MAXIMUM_GAP_DIST:
        if parent_section.in_x_axis_range(child_section):
            return True
    elif parent_section.x_difference(child_section) < MAXIMUM_GAP_DIST:
        if parent_section.in_y_axis_range(child_section):
            return True

    # elif parent_section.completely_above(child_section) or  parent_section.completely_below(child_section):
    #     if parent_section.y_difference(child_section) > MAXIMUM_GAP_DIST:
    #         return False
    #     if not parent_section.in_x_axis_range(child_section):
    #         return False
    # elif parent_section.in_y_axis_range(child_section):
    #     if parent_section.x_difference(child_section) > MAXIMUM_GAP_DIST:
    #         return False
    print("failed every case? how")
    return False


def calculate_long_edge(image: np.array) -> bool:
    """"""
    # determine all the edges in the image
    # if the image forms a loop(?) its a letter and we remove it
    # for the remaining edges, we determine the maximum possible length
    # and compare that length to the size of the image

    if image is None:
        return -1

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold = cv2.threshold(grayscale, 200, 255, cv2.THRESH_BINARY_INV)[1]
    contours = cv2.findContours(
        threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    contours = contours[0] if len(contours) == 2 else contours[1]

    longest_length_arr = [0]

    for cnt in contours:
        temp_thresh = cv2.drawContours(
            np.zeros_like(threshold), [cnt], -1, 255, 1
        )
        longest_val = corner_harris_impl(temp_thresh, cnt)
        longest_length_arr.append(longest_val)

    return max(longest_length_arr)


def corner_harris_impl(img_bin: np.array, cnt):
    dst = cv2.cornerHarris(img_bin, 2, 3, 0.04)
    cand = []
    for i, c in enumerate(np.argwhere(dst > 0.1 * np.max(dst)).tolist()):
        c = np.flip(np.array(c))
        if len(cand) == 0:
            cand.append(c)
        else:
            add = True
            for j, d in enumerate(cand):
                d = np.array(d)
                if np.linalg.norm(c - d) < 5:
                    add = False
                    break
            if add:
                cand.append(c)

    # Get indices of actual, nearest matching contour points
    corners = sorted(
        [np.argmin(np.linalg.norm(c - cnt.squeeze(), axis=1)) for c in cand]
    )

    # Extract edges from contour, and measure their lengths
    longest_val = 0
    for i_c, c in enumerate(corners):
        if i_c == len(corners) - 1:
            edge = np.vstack([cnt[c:, ...], cnt[0 : corners[0], ...]])
        else:
            edge = cnt[c : corners[i_c + 1], ...]

        length = cv2.arcLength(edge, False)
        longest_val = max(longest_val, length)
    return longest_val
