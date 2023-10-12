import cv2
import numpy as np
import easyocr
import math

import utilities.helpers.imageHelpers as imgutil
import utilities.helpers.stringHelpers as strutil

readers = {
    "japanese": easyocr.Reader(["ja"], gpu=False),
    # 'korean': easyocr.Reader(['ko', 'en'], gpu = True),
    # 'chinese_sim': easyocr.Reader(['ch_sim', 'en'], gpu = True),
}


def do_something(image, box_list):
    for box, text, confidence in box_list:
        (tl, tr, br, bl) = imgutil.unpack_box(box)
        x_min = tl[0]
        x_max = tr[0]
        y_min = tl[1]
        y_max = bl[1]

        result = readers["japanese"].recognize(
            image, [[x_min, x_max, y_min, y_max]], [box]
        )
        # print('Finding result')
        # print(result)
        print("[Done]")


def _draw_text_borders(image: np.array, borders_list: list) -> np.array:
    """ """
    if image is None or borders_list is None:
        return
    border_color = (0, 255, 0)
    border_pixel = 1

    for box, _, _ in borders_list:
        (tl, tr, br, bl) = box
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))

        cv2.rectangle(
            image, tl, br, color=border_color, thickness=border_pixel
        )
        # cv2.imshow('current rect', image)
        # cv2.waitKey()

    return image


def _draw_detect_borders(image, section):
    if image is None or section is None:
        return
    border_color = (0, 255, 0)
    border_pixel = 1
    for xmin, xmax, ymin, ymax in section:
        tl = (int(xmin), int(ymin))
        br = (int(xmax), int(ymax))

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
            image, width_ths=0.55, height_ths=0.55, paragraph=True
        )


def get_sections(
    image: np.array, source_lang: str = "japanese"
) -> (list, list):
    """"""
    if image is None:
        return
    horz, _ = readers[source_lang].detect(
        image,
        width_ths=0.55,
        height_ths=0.55,
    )
    return horz[0]


def confidence_average(confidence1, confidence2):
    """
    TODO: Improve this better
    """
    return (confidence1 + confidence2) / 2


def generate_section_details(section: list) -> list:
    return {"parent": section, "children": []}


def add_to_parent_section(parent: list, child: list) -> list:
    if "children" in parent:
        parent["children"].append(child)
        return parent
    else:
        raise ValueError("Did not provide valid parent")


def merge_two_sections(section1: list, section2: list) -> list:
    """"""
    (section1_box, section1_text, section1_conf) = section1
    (section2_box, section2_text, section2_conf) = section2

    (section1_tl, section1_tr, _, section1_bl) = imgutil.unpack_box(
        section1_box
    )
    (section2_tl, section2_tr, _, section2_bl) = imgutil.unpack_box(
        section2_box
    )

    merged_tl_x = min(section1_tl[0], section2_tl[0])
    merged_tr_x = max(section1_tr[0], section2_tr[0])
    merged_tl_y = min(section1_tl[1], section2_tl[1])
    merged_bl_y = max(section1_bl[1], section2_bl[1])
    merged_text = section2_text + section1_text
    merged_conf = confidence_average(section1_conf, section2_conf)
    merged_section = [
        [
            [merged_tl_x, merged_tl_y],  # top left corner
            [merged_tr_x, merged_tl_y],  # top right corner
            [merged_tr_x, merged_bl_y],  # bottom right corner
            [merged_tl_x, merged_bl_y],  # bottom left corner
        ],
        merged_text,
        merged_conf,
    ]

    return merged_section


def point_in_rectangle(point: list, rectangle: list) -> bool:
    (tl, tr, br, bl) = imgutil.unpack_box(rectangle)
    x1, y1, x2, y2 = tl[0], tl[1], br[0], br[1]
    x, y = point[0], point[1]

    if (x1 <= x and x <= x2) and (y1 <= y and y <= y2):
        return True
    return False


def overlaps(section1: list, section2: list) -> bool:
    """"""
    (section1_box, _, _) = section1
    (section2_box, _, _) = section2

    (section1_tl, section1_tr, section1_br, section1_bl) = imgutil.unpack_box(
        section1_box
    )
    (section2_tl, section2_tr, section2_br, section2_bl) = imgutil.unpack_box(
        section2_box
    )
    # Assume section 1's coordinates overlaps with section 2
    # Case1.1: There exists point inside the section2's rectangle.
    is_inside_section2 = (
        point_in_rectangle(section1_tl, section2)
        or point_in_rectangle(section1_tr, section2)
        or point_in_rectangle(section1_br, section2)
        or point_in_rectangle(section1_bl, section2)
    )
    if is_inside_section2:
        return True

    # Case1.2: There exists point inside section1's rectangle.
    is_inside_section1 = (
        point_in_rectangle(section2_tl, section1)
        or point_in_rectangle(section2_tr, section1)
        or point_in_rectangle(section2_br, section1)
        or point_in_rectangle(section2_bl, section1)
    )
    if is_inside_section1:
        return True

    # These two rectangles then dont overlap
    return False


def x_distance_diff_crisscross(section1: list, section2: list) -> float:
    (section1_box, section1_text, section1_conf) = section1
    (section2_box, section2_text, section2_conf) = section2

    (section1_tl, section1_tr, section1_br, section1_bl) = imgutil.unpack_box(
        section1_box
    )
    (section2_tl, section2_tr, section2_br, section2_bl) = imgutil.unpack_box(
        section2_box
    )
    # Lets assume the section 2 is right of section 1
    # we use section1's top_right_x, section2's top_left_x
    x_difference_right = abs(section1_tr[0] - section2_tl[0])

    # Lets assume the section 2 is left of section 1
    # we use section1's top_left_x, section2's top_right_x
    x_difference_left = abs(section1_tl[0], section2_tr[0])

    # the real difference will be the smaller value of these two
    # one of them will always be x_real_difference + box_width
    x_real_difference = min(x_difference_left, x_difference_right)

    return x_real_difference


def merge_close_sections(
    sections: list, MAX_DIST_DIFF: float, MIN_OVERLAP_PERCENT: float
) -> (list, list):
    """"""
    merged_sections = []
    merged_sections_details = []

    for basic_section in sections:
        is_basic_section_merged = False
        merge_section_index = 0

        for merge_section in merged_sections:
            if overlaps(basic_section, merge_section):
                # think about what cases are invalid when two boxes overlaps?
                # 1) if the two section's font size is completely different
                # 2) if the merged section's dimensions / image dimensions
                # is greater than 40% (?), we dont merge it...
                pass
            elif section_completely_above(basic_section, merge_section):
                pass
            elif section_completely_below(basic_section, merge_section):
                pass
            # they are in the similar y proximity
            elif distance_diff(basic_section, merge_section) <= MAX_DIST_DIFF:
                pass
            else:
                # should tech never reach here
                pass
            merge_section_index += 1

        if not is_basic_section_merged:
            merged_sections.append(basic_section)
            merged_sections_details.append(
                generate_section_details(basic_section)
            )
    return merged_sections, merged_sections_details


def _merge_overlapping_text_borders(boxlist: list) -> list:
    MAXIMUM_VERTICAL_DISTANCE = 2
    MAXIMUM_HORIZONTAL_DISTANCE = 2
    merged_box = []

    def _merge_vertical_overlapping_borders():
        index = 0
        for section in boxlist:
            if len(merged_box) == 0:
                merged_box.append(section)
            else:
                section_idx = 0
                is_section_merged = False
                for bigger_section in merged_box:
                    if vertical_overlap(
                        section, bigger_section
                    ) or vertical_overlap(bigger_section, section):
                        print("vertical overlap found")
                        merged_section = merge_sections(
                            section, bigger_section
                        )
                        merged_box[section_idx] = merged_section
                        is_section_merged = True
                        break
                    section_idx += 1

                # del section_idx
                # didnt find any section that overlaps with this section
                if not is_section_merged:
                    merged_box.append(section)
                index += 1

    def merge_sections(section1, section2):
        """ """
        (section1_box, section1_text, section1_conf) = section1
        (section2_box, section2_text, section2_conf) = section2

        (section1_tl, section1_tr, section1_br, section1_bl) = section1_box
        (section2_tl, section2_tr, section2_br, section2_bl) = section2_box

        section1_width = abs(section1_tl[0] - section1_tr[0])
        section2_width = abs(section2_tl[0] - section2_tr[0])
        section1_height = abs(section1_tl[1] - section1_bl[1])
        section2_height = abs(section2_tl[1] - section2_bl[1])

        merged_tl_x = min(section1_tl[0], section2_tl[0])
        merged_tr_x = max(section1_tr[0], section2_tr[0])
        merged_tl_y = min(section1_tl[1], section2_tl[1])
        merged_bl_y = max(section1_bl[1], section2_bl[1])

        section_confidence_avg = confidence_average(
            section1_conf, section2_conf
        )

        merged_section = [
            [
                [merged_tl_x, merged_tl_y],
                [merged_tr_x, merged_tl_y],
                [merged_tr_x, merged_bl_y],
                [merged_tl_x, merged_bl_y],
            ],
            section1_text + section2_text,
            section_confidence_avg,
        ]
        return merged_section

    def similar_size(width1, height1, width2, height2):
        """
        TODO: See the @UPDATE REQUIRED SECTION
        """
        TEMPORARY_MAXIMUM_DISTANCE_MUL = 3
        TEMPORARY_MAXIMUM_DISTANCE_DIFF = 250
        # @UPDATE REQUIRED
        # but it could be the case that width of small box is
        # many many times smaller than width of big box
        # and we dont want to merge them in a case like that
        small_width = min(width1, width2)
        small_height = min(height1, height2)

        large_width = max(width1, width2)
        large_height = max(height1, height2)

        if (
            small_width * TEMPORARY_MAXIMUM_DISTANCE_MUL >= large_width
            and small_height * TEMPORARY_MAXIMUM_DISTANCE_MUL >= large_height
        ):
            return True

        width_size_diff = large_width - small_width
        height_size_diff = large_height - small_height

        if (
            width_size_diff <= TEMPORARY_MAXIMUM_DISTANCE_DIFF
            and height_size_diff <= TEMPORARY_MAXIMUM_DISTANCE_DIFF
        ):
            return True

        return False

    def mostlyInsideSection(section1_box, section2_box):
        """ """
        # assume that section2 is strictly bigger than section1
        (section1_tl, section1_tr, section1_br, section1_bl) = section1_box
        (section2_tl, section2_tr, section2_br, section2_bl) = section2_box

        # box is mostly inside left side of section2
        left_inside_dist = abs(section2_tl[0] - section1_tr[0])
        left_outside_dist = abs(section2_tl[0] - section1_tl[0])

        if left_inside_dist <= left_outside_dist:
            return True

        # box is mostly inside right side of section2
        right_inside_dist = abs(section2_tr[0] - section1_tl[0])
        right_outside_dist = abs(section2_tr[0] - section1_tr[0])

        if right_inside_dist <= right_outside_dist:
            return True
        return False

    def vertical_overlap(section1, section2):
        """
        TODO: See the @UPDATE REQUIRED SECTION
        """
        (section1_box, _, _) = section1
        (section2_box, _, _) = section2

        (section1_tl, section1_tr, section1_br, section1_bl) = section1_box
        (section2_tl, section2_tr, section2_br, section2_bl) = section2_box
        section1_tr = list(map(int, section1_tr))
        section1_tl = list(map(int, section1_tl))
        section1_br = list(map(int, section1_br))
        section1_bl = list(map(int, section1_bl))
        section2_tr = list(map(int, section2_tr))
        section2_tl = list(map(int, section2_tl))
        section2_br = list(map(int, section2_br))
        section2_bl = list(map(int, section2_bl))

        section1_width = abs(section1_tl[0] - section1_tr[0])
        section2_width = abs(section2_tl[0] - section2_tr[0])
        section1_height = abs(section1_tl[1] - section1_bl[1])
        section2_height = abs(section2_tl[1] - section2_bl[1])

        # case1: assume the largebox is above small_box
        if section2_tl[1] <= section1_tl[1]:
            if section2_bl[1] >= section1_tl[1]:
                # compare x coordinates to see if they are in range
                if section1_tl[0] in range(
                    section2_bl[0], section2_br[0]
                ) or section1_tr[0] in range(section2_bl[0], section2_br[0]):
                    if similar_size(
                        section1_width,
                        section1_height,
                        section2_width,
                        section2_height,
                    ):
                        return True
                    # it could be the case that we are accidently lcapturing
                    # a small box already inside a much larger box
                    # if mostlyInsideSection(
                    #     section1_box, section2_box
                    # ) or mostlyInsideSection(section2_box, section1_box):
                    #     return True

        # case2: assume the largebox is below small_box
        else:
            if section2_tl[1] <= section1_bl[1]:
                if section1_bl[0] in range(
                    section2_tl[0], section2_tr[0]
                ) or section1_br[0] in range(section2_tl[0], section2_tr[0]):
                    if similar_size(
                        section1_width,
                        section1_height,
                        section2_width,
                        section2_height,
                    ):
                        return True
                    # if mostlyInsideSection(
                    #     section1_box, section2_box
                    # ) or mostlyInsideSection(section2_box, section1_box):
                    #     return True

        # if the vertical distance between them isn't too large
        # if the horizontal distance between them is not too large, and
        # if the size of the bigger parent wont increase by too much
        # then we can just consider merging them together

        MAXIMUM_HORIZONTAL_DIST_FOR_MERGE = 3

        # if section1_tl[1] in range(
        #     section2_tl[1], section2_bl[1]
        # ) or section1_bl[1] in range(section2_tl[1], section2_bl[1]):
        #     horizontal_dist = abs(section1_tr[0] - section2_tl[0])
        #     if horizontal_dist <= MAXIMUM_HORIZONTAL_DIST_FOR_MERGE:
        #         return True
        #     horizontal_dist = abs(section1_tl[0] - section2_tr[0])
        #     if horizontal_dist <= MAXIMUM_HORIZONTAL_DIST_FOR_MERGE:
        #         return True
        # if section2_tl[1] in range(
        #     section1_tl[1], section1_bl[1]
        # ) or section2_bl[1] in range(section1_tl[1], section1_bl[1]):
        #     horizontal_dist = abs(section1_tr[0] - section2_tl[0])
        #     if horizontal_dist <= MAXIMUM_HORIZONTAL_DIST_FOR_MERGE:
        #         return True
        #     horizontal_dist = abs(section1_tl[0] - section2_tr[0])
        #     if horizontal_dist <= MAXIMUM_HORIZONTAL_DIST_FOR_MERGE:
        #         return True

        return False

    _merge_vertical_overlapping_borders()
    return merged_box


def get_text_sections(image: np.array, source_lang: str) -> list:
    """ """
    return _get_text_borders(image, source_lang, configs={})
