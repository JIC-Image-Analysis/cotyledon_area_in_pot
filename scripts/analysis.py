"""penfiels_cotyledon_tray_area analysis."""

import os
import logging
import argparse

import numpy as np

import dtool

from jicbioimage.core.image import Image
from jicbioimage.core.transform import transformation
from jicbioimage.core.io import AutoName, AutoWrite

from jicbioimage.illustrate import AnnotatedImage

__version__ = "0.1.0"

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


def annotate(image, leafs, output_path):
    grayscale = np.mean(image, axis=2)
    ann = AnnotatedImage.from_grayscale(grayscale)
    ann[leafs] = image[leafs]

    area = np.sum(leafs)
    ann.text_at(
        "Area (pixels): {}".format(area),
        position=(10, 10),
        color=(255, 0, 255),
        size=132,
        antialias=False,
        center=False)

    with open(output_path, "wb") as fh:
        fh.write(ann.png())


def analyse_file(fpath, output_dir):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)

    image = identity(image)
    leafs = find_leafs(image)

    output_fname = os.path.basename(fpath).split(".")[0] + "_annotated.png"
    output_path = os.path.join(output_dir, output_fname)

    annotate(image, leafs, output_path)


def analyse_dataset(dataset_dir, output_dir):
    """Analyse all the files in the dataset."""
    dataset = dtool.DataSet.from_path(dataset_dir)
    logging.info("Analysing files in dataset: {}".format(dataset.name))
    for i in dataset.identifiers:
        fpath = dataset.item_path_from_hash(i)
        analyse_file(fpath, output_dir)


def main():
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_dir", help="Input dataset directory")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Write out intermediate images")
    args = parser.parse_args()

    if not os.path.isdir(args.dataset_dir):
        parser.error("Not a directory: {}".format(args.dataset_dir))

    # Create the output directory if it does not exist.
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    AutoName.directory = args.output_dir

    # Only write out intermediate images in debug mode.
    if not args.debug:
        AutoWrite.on = False

    # Setup a logger for the script.
    log_fname = "audit.log"
    log_fpath = os.path.join(args.output_dir, log_fname)
    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(filename=log_fpath, level=logging_level)

    # Log some basic information about the script that is running.
    logging.info("Script name: {}".format(__file__))
    logging.info("Script version: {}".format(__version__))

    analyse_dataset(args.dataset_dir, args.output_dir)


if __name__ == "__main__":
    main()
