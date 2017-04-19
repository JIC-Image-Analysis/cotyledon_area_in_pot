# penfiels_cotyledon_tray_area

## Introduction

This image analysis project has been setup to take advantage of a technology
known as Docker.

This means that you will need to:

1. Download and install the [Docker Toolbox](https://www.docker.com/products/docker-toolbox)
2. Build a docker image

Before you can run the image analysis in a docker container.


## Build a Docker image

Before you can run your analysis you need to build your docker image.  Once you
have built the docker image you should not need to do this step again.

A docker image is basically a binary blob that contains all the dependencies
required for the analysis scripts. In other words the docker image has got no
relation to the types of images that we want to analyse, it is simply a
technology that we use to make it easier to run the analysis scripts.

```
$ cd docker
$ bash build_docker_image.sh
$ cd ..
```

## Start a Docker container to run the image analysis in

The image analysis will be run in a Docker container.  The script
``run_docker_container.sh`` will drop you into an interactive Docker session.

```
$ bash run_docker_container.sh
[root@048bd4bd961c /]#
```


## Whole image analysis

Now you can run the image analysis.

```
[root@048bd4bd961c /]# python scripts/whole_image_analysis.py --debug data/dataset_dir output/
```

## Analyse area within a quadrilateral

Alternatively you can run the analysis on a dataset that has been marked up with
quadrilateral points using
[quadrilateral_point_clicker](https://github.com/JIC-Image-Analysis/quadrilateral_point_clicker).

```
[root@048bd4bd961c /]# python scripts/quadrilateral_analysis.py --debug data/dataset_dir output/
```
