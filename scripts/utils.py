"""penfiels_cotyledon_tray_area analysis."""

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
