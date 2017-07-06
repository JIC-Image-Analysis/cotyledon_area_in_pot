"""penfiels_cotyledon_tray_area analysis."""

import math

import PIL
import PIL.ImageDraw
import numpy as np

from jicbioimage.core.transform import transformation
from jicbioimage.core.io import AutoName

from jicbioimage.illustrate import AnnotatedImage


AutoName.prefix_format = "{:03d}_"


@transformation
def identity(image):
    """Return the image as is."""
    return image


@transformation
def green_minus_red(image):
    im = image[:, :, 1] - image[:, :, 0]
    red_gt_green = image[:, :, 0] > image[:, :, 1]
    im[red_gt_green] = 0
    return im


@transformation
def abs_threshold(image, cutoff):
    return image > cutoff



def find_leafs(image):
    leafs = green_minus_red(image)
    leafs = abs_threshold(leafs, 40)  # 30, 50
    return leafs


def scale(relative, dimension):
    return int(round(relative * dimension))


@transformation
def quadrilateral_mask_from_corners(image, corners):
    ydim, xdim = image.shape[:2]
    polygon = [
        (scale(corners[0]["x"], xdim), scale(corners[0]["y"], ydim)),
        (scale(corners[1]["x"], xdim), scale(corners[1]["y"], ydim)),
        (scale(corners[3]["x"], xdim), scale(corners[3]["y"], ydim)),
        (scale(corners[2]["x"], xdim), scale(corners[2]["y"], ydim)),
    ]
    img = PIL.Image.new("L", (xdim, ydim), 0)
    PIL.ImageDraw.Draw(img).polygon(polygon, outline=255, fill=255)
    return np.array(img, dtype=bool)


def ruler_length_in_pixels(image, points):
    ydim, xdim = image.shape[:2]
    x1 = points[0]["x"] * xdim
    y1 = points[0]["y"] * ydim
    x2 = points[1]["x"] * xdim
    y2 = points[1]["y"] * ydim
    xdiff = x1 - x2
    ydiff = y1 - y2
    dist2 = xdiff**2 + ydiff**2
    dist = math.sqrt(dist2)
    return int(round(dist))


@transformation
def apply_mask(image, mask):
    return image * mask


def annotate(image, leafs, area, output_path):
    grayscale = np.mean(image, axis=2)
    ann = AnnotatedImage.from_grayscale(grayscale)
    ann[leafs] = image[leafs]

    ann.text_at(
        "Area (pixels): {}".format(area),
        position=(10, 10),
        color=(255, 0, 255),
        size=132,
        antialias=False,
        center=False)

    with open(output_path, "wb") as fh:
        fh.write(ann.png())
