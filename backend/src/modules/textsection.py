"""
This module, textsection, contains two main classes, textsection and
parenttextsection. The details of each class will contain on its own respective
classes. 

Apart from the classes, this module also contains bounding box merging logics.
The reason for these functions to exist is because EasyOCR is not always able
to correctly merge the text bounding boxes. 

"""

from src.utilities.helpers.imageHelpers import unpack_box
import cv2
import math
import numpy as np


class textsection:
    """
    A class used to represent a textbox section in an image

    Attributes
    ----------
    text : str
        The string content of the textbox

    start_pos : list
        The start position of the textbox in the original image

    end_pos : list
        The end position of the textbox in the original image

    width : int
        The width of the bounding box

    height : int
        The height of the bounding box

    font_size : int
        The font size of the text in the bounding box

    font_type : str
        The name of the font. Default is Wild Words

    Methods
    -------
    set_text(text)
        Sets the textsection's text

    set_font_size(font_size)
        Sets the font size of the text in the section

    set_font_type(font_type)
        Sets the font style of the text in the section

    set_position(position)
        Sets the position of the bounding box in the section
    """

    def __init__(
        self, text, position, font_size, font_type="Wild Words"
    ) -> None:
        """
        Parameters
        ----------
        text : str
            The text of the textsection class

        position : list
            The position of the bounding box. The position must only contain
            4 values, [xmin, xmax, ymin, ymax]

        font_size : int
            The size of the text font

        font_type : str
            The name of the text font
        """

        self.set_text(text)
        self.set_font_size(font_size)
        self.set_font_type(font_type)
        self.set_position(position)

    def set_text(self, text: str) -> None:
        """Sets the textsection's text

        Parameters
        ----------
        text : str
            The text of the textsection class
        """

        self.text = text

    def set_font_size(self, font_size: int) -> None:
        """Sets the textsection's font size

        Parameters
        ----------
        font_size : int
            The font size of the text in integer
        """

        self.font_size = font_size

    def set_font_type(self, font_type: str = "Wild Words") -> None:
        """Sets the textsection's font type

        Parameters
        ----------
        font_size : str, optional
            The font type of the text in string. Default is "Wild Words"
        """

        self.font_type = font_type

    # TODO: Currently we are rounding down all the coordinates. Do we need this
    # and do we need to be rounding down/up/or conditionally?
    def set_position(self, position: list) -> None:
        """Sets the textsection's starting and ending positions and also the
        length and width of the bounding box

        Parameters
        ----------
        position : list
            The position of the bounding box. The position must only contain
            4 values, [xmin, xmax, ymin, ymax]
        """

        (x_min, x_max, y_min, y_max) = map(math.floor, position)

        self.start_pos = [x_min, y_min]
        self.end_pos = [x_max, y_max]
        self.width = x_max - x_min
        self.height = y_max - y_min

    def __str__(self) -> str:
        """The to_string representation of the textsection class"""

        content = f"text={self.text}, start=[{self.start_pos[0]}, "
        content += f"{self.start_pos[1]}], end=[{self.end_pos[0]}, "
        content += f"{self.end_pos[1]}], width={self.width}, "
        content += f"height={self.height}, font-size={self.font_size}, "
        content += f"font-type={self.font_type}]"

        return content


class parenttextsection:
    """
    A class used to represent the merged textsections

    Attributes
    ----------
    text : str
        The section's combined text

    original_section : section
        The section's original props before it is merged with other sections

    width : int
        The merged section's bounding box's width in integer

    height : int
        The merged section's bounding box's height in integer

    start_pos : int
        The merged section's bounding box's starting position in original image

    end_pos : int
        The merged section's bounding box's ending position in original image

    font_size : int
        The merged section's font size in pixels

    font_type : str
        The merged section's font type in string.

    children : list
        List of textsections that are merged in the parenttextsection

    Methods
    -------
    add_section(section)
        Merges a section to the parenttextsection

    similar_fonts(section)
        Determines if other section contains same fonts as parenttextsection

    overlaps(section)
        Determines if other section's coordinates overlaps parenttextsection

    is_merging_too_big(section, image)
        Determines if merging section increase parenttextsection size too much

    draw_section(image)
        Adds borders around the section based on starting and ending position

    completely_above(section)
        Determines if the parenttextsection is completely above other section

    completely_below(section)
        Determines if the parenttextsection is completely below other section

    in_y_axis_range(section)
        Determines if the parenttextsection is neither completely above nor
        completely below other section

    completely_left(section)
        Determines if the parenttextsection is completely left of other section

    completely_right(section)
        Determines if the parenttextsection is completely right of othersection

    in_x_axis_range(section)
        Determines if the parenttextsection is neither completely left nor
        completely right of other section

    y_difference(section)
        Determines the vertical difference from section to parenttextsection

    x_difference(section)
        Determines the horizontal difference from section to parenttextsection
    """

    def __init__(self, section: textsection) -> None:
        """
        Parameters
        ----------
        section : textsection
            The section class to be merged to parenttextsection
        """

        self.original_section = section
        self.text = section.text

        self.width = section.width
        self.height = section.height
        self.start_pos = section.start_pos
        self.end_pos = section.end_pos

        self.font_size = section.font_size
        self.font_type = section.font_type

        self.children = []

    def __str__(self) -> str:
        """The to_string representation of the parenttextsection class"""

        content = "[\n"
        content += f"\tParent=[text={self.text}, start=[{self.start_pos[0]}, "
        content += f"{self.start_pos[1]}], end=[{self.end_pos[0]}, "
        content += f"{self.end_pos[1]}], width={self.width}, "
        content += f"height={self.height}, font-size={self.font_size}, "
        content += f"font-type={self.font_type}]\n"
        content += f"\tOriginal=[{self.original_section.__str__()}]\n"
        content += f"\tChildren=[\n"

        for child in self.children:
            content += f"\t\t[{child.__str__()}],\n"
        content += "\n\t]\n]"

        return content

    def add_section(self, section: textsection) -> None:
        """
        Merge a section into the parenttextsection

        Parameters
        ----------
        section : textsection
            The textsection to merge to the parenttextsection
        """
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
        self.text += " " + section.text

    # TODO: Currently we are comparing font sizes if they are within 5 sizes
    # less and more than the parenttextsection's font size. This is not a good
    # way to compare sizes. Figure out a better way.
    def similar_fonts(self, section: textsection) -> bool:
        """
        Determine if the parenttextsection has similar font size as section

        Parameters
        ----------
        section : textsection
            The textsection to compare font size to

        Returns
        -------
        bool
            True if section's font_size is within range of parenttextsection's
            font_size
            False otherwise
        """

        return section.font_size in range(
            self.font_size - 5, self.font_size + 5
        )

    # TODO: Change the way overlaps function works. Right now, it takes in
    # two rectangular boxes and determines if corners lies inside the boxes,
    # instead check for overlaps using start_x, start_y end_x, end_y only.
    def overlaps(self, section: textsection) -> bool:
        section1 = generate_box(self.start_pos, self.end_pos)
        section2 = generate_box(section.start_pos, section.end_pos)

        return is_section_overlap(section1, section2)

    # TODO: When is it too big to merge to boxes? Currently we compare the
    # merged box's width and height to the original image and if ratio is > 0.5
    # we consider it to be a big. Change this and find out a better way to
    # determine whether merging is too big or not
    def is_merging_too_big(
        self, section: textsection, image: np.array
    ) -> bool:
        """
        Determines if merging another section is too large or not

        Parameters
        ----------
        section : textsection
            The textsection that is merging into parenttextsection

        image : np.array
            The cv2 image to compare the ratio to

        Returns
        -------
        bool
            True if merging two sections results in too large bounding box
            False otherwise
        """

        mstart, mend = merge_dimensions(
            self.start_pos, self.end_pos, section.start_pos, section.end_pos
        )
        mwidth = abs(mend[0] - mstart[0])
        mheight = abs(mend[1] - mstart[1])
        imgheight, imgwidth, _ = image.shape
        widthratio = mwidth / imgwidth
        heightratio = mheight / imgheight

        if widthratio > 0.5 or heightratio > 0.5:
            return True
        return False

    def draw_section(self, image: np.array) -> np.array:
        """
        Draw green rectangular box around the bounding box in the image

        Parameters
        ----------
        image : np.array
            The cv2 image to draw the rectangular bounding box in

        Returns
        -------
        np.array
            The cv2 image after bounding box is added
        """

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
        """
        Determines if the parenttextsection is strictly above textsection

        Parameters
        ----------
        section : textsection
            The textsection to compare its position with

        Returns
        -------
        bool
            True if parenttextsection is strictly above the passed textsection
            False otherwise

        """

        return self.end_pos[1] < section.start_pos[1]

    def completely_below(self, section: textsection) -> bool:
        """
        Determines if the parenttextsection is strictly below textsection

        Parameters
        ----------
        section : textsection
            The textsection to compare its position with

        Returns
        -------
        bool
            True if parenttextsection is strictly below the passed textsection
            False otherwise
        """

        return self.start_pos[1] > section.end_pos[1]

    def in_y_axis_range(self, section: textsection) -> bool:
        """
        Determines if the parenttextsection is within the yaxis range

        Parameters
        ----------
        section : textsection
            The textsection to compare its position with

        Returns
        -------
        bool
            True if parenttextsection is within yaxis range of textsection
            False otherwise
        """

        return not self.completely_above(
            section
        ) and not self.completely_below(section)

    def completely_left(self, section: textsection) -> bool:
        """
        Determines if the parenttextsection is strictly left of textsection

        Parameters
        ----------
        section : textsection
            The textsection to compare its position with

        Returns
        -------
        bool
            True if parenttextsection is strictly left of passed textsection
            False otherwise
        """

        return self.end_pos[0] < section.start_pos[0]

    def completely_right(self, section: textsection) -> bool:
        """
        Determines if the parenttextsection is strictly right of textsection

        Parameters
        ----------
        section : textsection
            The textsection to compare its position with

        Returns
        -------
        bool
            True if parenttextsection is strictly right of passed textsection
            False otherwise
        """

        return self.start_pos[0] > section.end_pos[0]

    def y_difference(self, section: textsection) -> int:
        """
        Determines vertical difference between parenttextsection and section

        Parameters
        ----------
        section : textsection
            The textsection to get the vertical differnece with

        Returns
        -------
        int
            The vertical difference in pixels
        """

        above_diff = abs(self.end_pos[1] - section.start_pos[1])
        below_diff = abs(section.end_pos[1] - self.start_pos[1])

        return min(above_diff, below_diff)

    def in_x_axis_range(self, section: textsection) -> bool:
        """
        Determines if the parenttextsection is within the xaxis range

        Parameters
        ----------
        section : textsection
            The textsection to compare its position with

        Returns
        -------
        bool
            True if parenttextsection is within xaxis range of textsection
            False otherwise
        """

        return not self.completely_left(section) and not self.completely_right(
            section
        )

    def x_difference(self, section: textsection) -> int:
        """
        Determines horizontal difference between parenttextsection and section

        Parameters
        ----------
        section : textsection
            The textsection to get the horizontal differnece with

        Returns
        -------
        int
            The horizontal difference in pixels
        """

        right_diff = abs(self.end_pos[0] - section.start_pos[0])
        left_diff = abs(section.end_pos[0] - self.start_pos[0])

        return min(left_diff, right_diff)


# TODO: All the positions below should be using a Point class to represent
# the point, not a list object. Add this feature
def merge_dimensions(
    start_pos1: list, end_pos1: list, start_pos2: list, end_pos2: list
) -> list:
    """
    Merges the the two bounding boxes

    Parameters
    ----------
    start_pos1 : list
        The start position of first bounding box

    end_pos1 : list
        The end position of first bounding box

    start_pos2 : list
        The start position of second bounding box

    end_pos2 : list
        The end position of second bounding box

    Returns
    -------
    list
        The merged point represented in list. The list will conotain two
        points, [merged_start_pos, merged_end_pos]
    """

    mstart_x = min(start_pos1[0], start_pos2[0])
    mstart_y = min(start_pos1[1], start_pos2[1])
    mend_x = max(end_pos1[0], end_pos2[0])
    mend_y = max(end_pos1[1], end_pos2[1])

    return [mstart_x, mstart_y], [mend_x, mend_y]


# TODO: We no longer use box representation, but rather just start and end pos
# Revamp this method so that we only use start and end pos of each section
def is_section_overlap(section1: list, section2: list) -> bool:
    """
    Determines if two bounding boxes overlaps each other

    Parameters
    ----------
    section1 : list
        The bounding box of the first section. The bounding box is list of 4
        points of format [top_left, top_right, bottom_right, bottom_left]

    section2 : list
        The bounding box of the second section. The bounding box is list of 4
        points of format [top_left, top_right, bottom_right, bottom_left]

    Returns
    -------
    bool
        True if a section overlaps another, False otherwise
    """

    section1_tl, section1_tr, section1_br, section1_bl = unpack_box(section1)

    is_inside_section2 = (
        is_point_in_rectangle(section1_tl, section2)
        or is_point_in_rectangle(section1_tr, section2)
        or is_point_in_rectangle(section1_br, section2)
        or is_point_in_rectangle(section1_bl, section2)
    )

    if is_inside_section2:
        return True

    section2_tl, section2_tr, section2_br, section2_bl = unpack_box(section2)

    is_inside_section1 = (
        is_point_in_rectangle(section2_tl, section1)
        or is_point_in_rectangle(section2_tr, section1)
        or is_point_in_rectangle(section2_br, section1)
        or is_point_in_rectangle(section2_bl, section1)
    )
    if is_inside_section1:
        return True

    return False


def is_point_in_rectangle(point: list, rectangle: list) -> bool:
    """
    Determines if a point lies inside a rectangle

    Parameters
    ----------
    point : list
        The point to compare with. The point is of format [x, y]

    rectangle : list
        The bounding box of the section. The rectangle is list of 4
        points of format [top_left, top_right, bottom_right, bottom_left]

    Returns
    -------
    bool
        True if a point lies in the rectangle, False otherwise
    """

    (tl, _, br, _) = unpack_box(rectangle)
    x1, y1, x2, y2 = tl[0], tl[1], br[0], br[1]
    x, y = point[0], point[1]

    if (x1 <= x and x <= x2) and (y1 <= y and y <= y2):
        return True
    return False


def generate_box(start_pos: list, end_pos: list) -> list:
    """
    Generates a box based of start_pos and end_pos points

    Parameters
    ----------
    start_pos : list
        The starting position of the point. It is of format [x, y]

    end_pos : list
        The ending position of the point. It is of format [x, y]

    Returns
    -------
    list
        Creates a bounding box of 4 points. The bounding box of points is of
        the format [top_left, top_right, bottom_right, bottom_left]
    """

    start_x, start_y = start_pos[0], start_pos[1]
    end_x, end_y = end_pos[0], end_pos[1]

    return [start_pos, [end_x, start_y], end_pos, [start_x, end_y]]


# TODO: How exactly should the maximum gap even be calculated? What determines
# a good merge? Need to figure out a better way to do this merging
def should_merge_sections(
    parent_section: parenttextsection,
    child_section: textsection,
    MAXIMUM_GAP_DIST: int,
    image: np.array,
) -> bool:
    """
    Determines if two section should be merged together or not

    Parameters
    ----------
    parent_section : parenttextsection
        The bigger section to add smaller sections inside

    child_section : textsection
        The smaller section that is trying to get merged

    MAXIMUM_GAP_DIST : int
        The maximum allowed gap between the two sections. It is the maximum
        gap allowed in both horizontal and vertical direction in pixels

    image : np.array
        The cv2 image that contains both of the sections

    Returns
    -------
    bool
        True if two sections can be merged successfully
        False otherwise
    """

    if parent_section.is_merging_too_big(child_section, image):
        return False
    if parent_section.overlaps(child_section):
        return True
    elif parent_section.y_difference(child_section) < MAXIMUM_GAP_DIST:
        if parent_section.in_x_axis_range(child_section):
            return True
    elif parent_section.x_difference(child_section) < MAXIMUM_GAP_DIST:
        if parent_section.in_y_axis_range(child_section):
            return True
    return False
