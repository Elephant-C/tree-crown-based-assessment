# Tree crown polygon-based assessment for airborne LiDAR individual tree segmentation methods #

 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
 
## Overview ##
The repository was developed by Yujie Cao, in close collaborations with [Tobias. D Jackson](https://github.com/TobyDJackson), [James Ball](https://github.com/PatBall1), during his visiting at Forest Conservation Group led by professor [David A. Coomes](https://scholar.google.com/citations?user=CXkjEhIAAAAJ&hl=en&oi=ao). The group is part of the University of Cambridge [Conservation Research Institute](https://www.conservation.cam.ac.uk/). 

This repository conducts robust inter-comparison for state-of-the-art airborne lidar point cloud based individual tree segmentation algorithms ([Dalponte2016](https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.12575), [Dalponte2016+](https://www.sciencedirect.com/science/article/pii/S0034425717301098), [li2012](https://www.ingentaconnect.com/content/asprs/pers/2012/00000078/00000001/art00006), and [AMS3D](https://www.sciencedirect.com/science/article/abs/pii/S0034425716302292)) in temperate forest (Wytham Woods in the UK) and tropical rainforests(Sepilok Forest in Sabah, Maylaysia). For more information about this work, please refer to: *__Tree segmentation in airborne laser scanning
data is only accurate for canopy trees.__*

__If you use code from this repository in your work, please cite the following paper in a proper way:__

*Yujie Cao, James G C Ball, David A. Coomes, Leon Steinmeier, Nikolai Knapp, Phil Wilkes, Kim Calders, Andrew Burt, Mathias Disney, Yi Lin, and Tobias D. Jackson. Tree segmentation in airborne laser scanning
data is only accurate for canopy trees.* (*__Pre-print DOI__* :https://doi.org/10.1101/2022.11.29.518407).

## Requirement ##
+ Python $\geqslant$ 3.7.12
+ [Open3d](http://www.open3d.org/) $\geqslant$ 0.15.1. Note 0.16.0 would lead to menmory leak issue like zsh: segmentation fault.
+ [Laspy](https://laspy.readthedocs.io/en/latest/index.html)
+ Numpy
+ Pandas
+ [Shapely](https://shapely.readthedocs.io/en/stable/manual.html)
+ [lidR](https://github.com/r-lidar/lidR) $\geqslant$ 4.0.0
+ [Fiona](https://github.com/Toblerity/Fiona)
+ multiprocessing
+ tqdm
+ pickle

## Organization ##
```
├── README.md
├── utils                                   <- Basic dependency code demoe for Predicted and benchmark polygon matching
|   ├── Evaluation.py
|   ├── rand_cmap.py
|   ├── LabelCorrect.py            
├── Algorithm implementartion
|   ├── Dalponte2016plus.R                  <- Implement Dalponte2016 within parameter space and the output can be either .csv or .hdf5
|   ├── Dalponte2016plus_areaCrop.R         <- Batchly core area filtering for predictions from Dalponte2016 
├── Assessment metrics calculation              
|   ├── dalponte2016plus_p_r_f1.py
├── Make figures and visualization   
|   ├── p_r_f_matrix.py                     <- Calculate matrix plot for precision, recall and F1 score                   
|   ├── p_r_f1_height.py                    <- Calculate matrix plot for precision, recall and F1 score           
|   ├── p_r_f1_Tau.py
|   ├── allometry_scatter.py
├── run.py                                  <- Implement the whole pipline                   
└── requirements
```

## Workfolow ##

There are four main steps in the framework:

+ Core Area Filtering
+ Confidence score voting for single predicted tree crown
+ Predicted and benchmark crown polygon matching
+ Precision, Recall and F1 Score calculation

<p align="center">
<img width="300" align="center" alt="predictions" src= ./Figures/assessment_strategy.png>
</p>

## Main Result ##
<p align="center">
<img width="500" align="center" alt="predictions" src= ./Figures/sepilok_p_r_f1_height.png>
</p>

<p align="center">
<img width="500" align="center" alt="predictions" src= ./Figures/allometry_IoU_scatter.png>
</p>

## USPS ##
Include more fucntions and establish a unversial framework to assess and then compare both deep learning ITS methods and traditional methods under the same standard.

## Other ##
