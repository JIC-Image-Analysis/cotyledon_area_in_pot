"""penfiels_cotyledon_tray_area analysis."""

import os
import logging
import argparse

import numpy as np

import dtool

from jicbioimage.core.image import Image
from jicbioimage.core.io import AutoName, AutoWrite

from utils import (
    identity,
    quadrilateral_mask_from_corners,
    find_leafs,
    annotate,
    apply_mask,
)


__version__ = "0.1.0"


def analyse_file(fpath, quadrilateral, output_dir):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)

    image = identity(image)
    mask = quadrilateral_mask_from_corners(image, quadrilateral)

    leafs = find_leafs(image)
    leafs = apply_mask(leafs, mask)

    output_fname = os.path.basename(fpath).split(".")[0] + "_annotated.png"
    output_path = os.path.join(output_dir, output_fname)

    area = int(np.sum(leafs))
    annotate(image, leafs, area, output_path)
    return area


def analyse_dataset(dataset_dir, output_dir):
    """Analyse all the files in the dataset."""
    dataset = dtool.DataSet.from_path(dataset_dir)
    logging.info("Analysing files in dataset: {}".format(dataset.name))

    quadrilateral_points = dataset.overlays["quadrilateral_points"]

    csv_fpath = os.path.join(output_dir, "summary.csv")
    with open(csv_fpath, "w") as csv_fh:

        csv_fh.write("identifier,image,tray,area\n")

        for i in dataset.identifiers:

            quadrilateral = quadrilateral_points[i]

            rel_path = dataset.item_from_hash(i)["path"]
            tray = os.path.dirname(rel_path)
            image_out_dir = os.path.join(output_dir, tray)
            if not os.path.isdir(image_out_dir):
                os.mkdir(image_out_dir)

            fpath = dataset.item_path_from_hash(i)
            area = analyse_file(fpath, quadrilateral, image_out_dir)

            csv_row = [i, rel_path, tray, str(area)]
            csv_line = ",".join(csv_row)
            csv_fh.write(csv_line + "\n")


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
