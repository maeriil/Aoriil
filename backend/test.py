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
        print("its twice bigger?")
        return True

    width_size_diff = large_width - small_width
    height_size_diff = large_height - small_height

    if (
        width_size_diff <= TEMPORARY_MAXIMUM_DISTANCE_DIFF
        and height_size_diff <= TEMPORARY_MAXIMUM_DISTANCE_DIFF
    ):
        print("size diff is less than threshold")
        return True

    return False


def mostlyInsideSection(section1_box, section2_box):
    """ """
    print("mostly inside invoked")
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

    section1_width = abs(section1_tl[0] - section1_tr[0])
    section2_width = abs(section2_tl[0] - section2_tr[0])
    section1_height = abs(section1_tl[1] - section1_bl[1])
    section2_height = abs(section2_tl[1] - section2_bl[1])

    # case1: assume the largebox is above small_box
    if section2_tl[1] <= section1_tl[1]:
        print("reached case 1")
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
                    print("similar size?")
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
                    print("similar size?")
                    return True
                if mostlyInsideSection(
                    section1_box, section2_box
                ) or mostlyInsideSection(section2_box, section1_box):
                    return True
    return False


points = [
    [[[44, 528], [116, 528], [116, 708], [44, 708]], "1", 0.42709992154503773],
    [[[42, 626], [68, 626], [68, 690], [42, 690]], "孝", 0.001047304776033764],
    [
        [[400, 84], [478, 84], [478, 152], [400, 152]],
        "なんはわなは言臨あ",
        0.8401061424343824,
    ],
    [
        [[398, 144], [452, 144], [452, 194], [398, 194]],
        "よて",
        0.9828370937364521,
    ],  # 7
    [
        [[73, 19], [539, 19], [539, 63], [73, 63]],
        "製郷‥《88町郷豊昌町@ぼ盟國",
        3.258755392981364e-06,
    ],
    [[[14, 50], [75, 50], [75, 639], [14, 639]], "1", 0.06588143091232812],
    [
        [[400, 84], [476, 84], [476, 110], [400, 110]],
        "言臨あ",
        0.3669572766838158,
    ],
    [
        [[400, 104], [476, 104], [476, 130], [400, 130]],
        "わなは",
        0.9995184434056272,
    ],
    [
        [[400, 124], [478, 124], [478, 152], [400, 152]],
        "なんは",
        0.9969744248240433,
    ],
    [
        [[939, 107], [999, 107], [999, 187], [939, 187]],
        "き",
        0.05805557562075592,
    ],
    [
        [[116, 146], [230, 146], [230, 176], [116, 176]],
        "ま信な証",
        0.9815359115600586,
    ],
    [
        [[112, 168], [232, 168], [232, 224], [112, 224]],
        "荒ら先親",
        0.000876924314070493,
    ],
    [
        [[840, 138], [938, 138], [938, 294], [840, 294]],
        "農",
        0.008969900807498599,
    ],
    [
        [[142, 218], [198, 218], [198, 244], [142, 244]],
        "れば",
        0.9636864940017271,
    ],
    [
        [[598, 415], [646, 415], [646, 556], [598, 556]],
        "当",
        0.0008778453835454059,
    ],
]

print(vertical_overlap(points[0], points[1]))

(sec1, _, _) = points[0]
(sec2, _, _) = points[1]
print(mostlyInsideSection(sec2, sec1))
print(similar_size(points[0], points))
