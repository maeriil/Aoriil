import cv2
import numpy as np
import easyocr
import math

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


def _get_text_borders(
    image: np.array, source_lang: str = "japanese", configs: dict = {}
) -> list:
    """ """
    if image is None:
        return
    if not configs:
        return readers[source_lang].readtext(
            image,
            width_ths=0.55,
            height_ths=0.55,
        )


def confidence_average(confidence1, confidence2):
    """
    TODO: Improve this better
    """
    return (confidence1 + confidence2) / 2


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
                    if mostlyInsideSection(
                        section1_box, section2_box
                    ) or mostlyInsideSection(section2_box, section1_box):
                        return True

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
                    if mostlyInsideSection(
                        section1_box, section2_box
                    ) or mostlyInsideSection(section2_box, section1_box):
                        return True

        # if the vertical distance between them isn't too large
        # if the horizontal distance between them is not too large, and
        # if the size of the bigger parent wont increase by too much
        # then we can just consider merging them together

        MAXIMUM_HORIZONTAL_DIST_FOR_MERGE = 3

        if section1_tl[1] in range(
            section2_tl[1], section2_bl[1]
        ) or section1_bl[1] in range(section2_tl[1], section2_bl[1]):
            horizontal_dist = abs(section1_tr[0] - section2_tl[0])
            if horizontal_dist <= MAXIMUM_HORIZONTAL_DIST_FOR_MERGE:
                return True
            horizontal_dist = abs(section1_tl[0] - section2_tr[0])
            if horizontal_dist <= MAXIMUM_HORIZONTAL_DIST_FOR_MERGE:
                return True
        if section2_tl[1] in range(
            section1_tl[1], section1_bl[1]
        ) or section2_bl[1] in range(section1_tl[1], section1_bl[1]):
            horizontal_dist = abs(section1_tr[0] - section2_tl[0])
            if horizontal_dist <= MAXIMUM_HORIZONTAL_DIST_FOR_MERGE:
                return True
            horizontal_dist = abs(section1_tl[0] - section2_tr[0])
            if horizontal_dist <= MAXIMUM_HORIZONTAL_DIST_FOR_MERGE:
                return True

        return False

    _merge_vertical_overlapping_borders()
    return merged_box


def get_text_sections(image: np.array, source_lang: str) -> list:
    """ """
    return _get_text_borders(image, source_lang, configs={})
