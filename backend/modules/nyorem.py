import cv2
import numpy as np
import os


# does exact same as my current implementation
# Binarize an image
def binarize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]
    # _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Apply Errosion then dialation using morphologyEx
    tempImg = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    # Invert the image colours
    tempImg = 255 - tempImg
    return tempImg


# Find the contours (rectangles) of text in an image
def find_contours_text(img, kernel_size, verbose=False, sort_key=None):
    # binarize
    binary = binarize(img)

    # dilation
    kernel = np.ones(kernel_size, dtype=np.uint8)
    dilation = cv2.dilate(binary, kernel, iterations=1)
    if verbose:
        cv2.imshow("dilation", dilation)
        cv2.waitKey(0)

    # find contours
    ctrs, _ = cv2.findContours(
        dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if sort_key is None:
        sort_key = lambda ctr: cv2.boundingRect(ctr)[0]
    sorted_ctrs = sorted(ctrs, key=sort_key)

    return sorted_ctrs


# Draw contours (rectanglers) over a given image
def draw_contours(ctrs, img, w_rect=2, fname=None, verbose=False):
    img_contours = img.copy()
    for i, ctr in enumerate(ctrs):
        x, y, w, h = cv2.boundingRect(ctr)
        cv2.rectangle(
            img_contours, (x, y), (x + w, y + h), (0, 255, 0), w_rect
        )
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            img_contours,
            str(i),
            (x + w // 2, y + h // 2),
            font,
            1,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )
        # cv2.putText(img_contours, str(x), (x + w//4, y + h//4), font, 1, (255, 0, 0), 5, cv2.LINE_AA)
    if fname is not None:
        cv2.imwrite(fname, img_contours)
    if verbose:
        cv2.imshow("contours", img_contours)
        cv2.waitKey(0)


# Get the rectangular box corresponding to a contour
def get_rect(img, ctr):
    x, y, w, h = cv2.boundingRect(ctr)
    return img[y : y + h, x : x + w]


# Find big sections of text in an image
def find_sections(img, verbose=False, dirname="results"):
    img_h, img_w = img.shape[:2]

    binary = binarize(img)
    if verbose:
        cv2.imshow("binary", binary)
        cv2.waitKey(0)

    sections = []
    size = (10, 100)

    # Crop the image a little to avoid outliers on the side of the page
    offsets = (2, 20)
    img = img[offsets[0] : -offsets[0], offsets[1] : -offsets[1]]

    sort_key = lambda ctr: cv2.boundingRect(ctr)[1]
    ctrs = find_contours_text(img, size, verbose=verbose, sort_key=sort_key)
    draw_contours(ctrs, img, w_rect=2, verbose=verbose)
    ii = 0
    for ctr in ctrs:
        _, _, w, h = cv2.boundingRect(ctr)
        ratio_w, ratio_h = w / img_w, h / img_h
        if ratio_h > 0.1:
            # if ratio_w > 0.25:
            section = get_rect(img, ctr)
            sections.append(section)
            cv2.imwrite("{}/section{}.png".format(dirname, ii), section)
            ii += 1

    return sections


# Sort contours left from right, top to bottom
def sort_contours(ctrs):
    threshold = 10
    threshold = 1

    # Find columns (sort by x)
    ctrs = sorted(ctrs, key=lambda ctr: -cv2.boundingRect(ctr)[0])
    cols = []
    col = []
    prev = cv2.boundingRect(ctrs[0])[0]
    for i, ctr in enumerate(ctrs):
        x, _, _, _ = cv2.boundingRect(ctr)
        if abs(x - prev) >= threshold:
            cols.append(col)
            col = []
        col.append(i)
        prev = x
    if col:
        cols.append(col)

    # Sort rectangles in columns (sort by y)
    sorted_ctrs = []
    for col in cols:
        col_ctrs = [ctrs[i] for i in col]
        sorted_col_ctrs = sorted(
            col_ctrs, key=lambda ctr: cv2.boundingRect(ctr)[1]
        )
        sorted_ctrs.append(sorted_col_ctrs)

    sorted_ctrs = flatten(sorted_ctrs)

    return sorted_ctrs


# Flatten a list of lists
def flatten(lst):
    return [item for sublist in lst for item in sublist]


# Find elements of text inside a section
def find_text(section, verbose=False, section_idx=None, dirname="results"):
    binary = binarize(section)
    if section_idx is None:
        section_idx = np.random.randint(10)

    if verbose:
        cv2.imshow("input_section", binary)

    # TODO: automate finding text width
    text_width = 35
    size = (text_width // 2, 10)

    ctrs = find_contours_text(section, size, verbose=verbose, sort_key=None)
    ctrs = sort_contours(ctrs)

    fname = "{}/section{}_annotated.png".format(dirname, section_idx)
    draw_contours(ctrs, section, w_rect=2, fname=fname, verbose=verbose)

    text = []
    for i, ctr in enumerate(ctrs):
        x, y, w, h = cv2.boundingRect(ctr)
        if w <= 30:
            continue
        text.append(ctr)

        txt = get_rect(section, ctr)
        section_dirname = "{}/section{}".format(dirname, section_idx)
        if not os.path.isdir(section_dirname):
            os.mkdir(section_dirname)
        cv2.imwrite(
            "{}/section{}/text{}.png".format(dirname, section_idx, i), txt
        )

    return text


# Find text in an image
def analyse_image(img, verbose=False, dirname="results"):
    sections = find_sections(img, verbose=verbose, dirname=dirname)
    # text = []

    for i, section in enumerate(sections):
        find_text(section, verbose=verbose, section_idx=i, dirname=dirname)

    return sections
