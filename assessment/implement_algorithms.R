#' This R script is to conduct grid search for inter-comparison of 4 state-of-the-art individual tree segmentation algorithms
#' Codes are wrapped as functions, you can call these function in your scripts.
#' @author Yujie Cao
#' for more information, please refer to our paper
#' @references Tree segmentation in airborne laser scanning data is only accurate for canopy trees.
#'Pre-print DOI :https://doi.org/10.1101/2022.11.29.518407.

library(lidR)
library(dplyr)
library(sf)

#' Implement AMS3D within H2CH & H2CD parameter space
#' @name AMS3D
#' @param data_path character. path for point cloud data.
#' @param boundary_path character. path for core area boundary shapefile data.
#' @param out_path charcter. path for exporting segmentation point clouds of core area.
#' @param H2CD list. Height and Crown Diameter ratio parameter to determine kernel bandwidth of mean-shifting process.
#' @param H2CH list. Height and Crown Height ratio parameter to determine kernel bandwidth of mean-shifting process.
ams3d <- function(data_path, boundary_path, out_path){
  library(crownsegmentr)
  # data_path <-  '/Volumes/T7/Data/New_Sepilok/ALS_xyzconfi.las'
  print(paste("input path is:", data_path))
  point_cloud <- readLAS(data_path) #, select = "xyz") #
  # boundary_path <- '/Volumes/T7/Data/New_Sepilok/Boundary_shp/concave_hull.shp'
  boundary <- sf::st_read(boundary_path)
  boundary_poly <- boundary$geometry
  H2CD <- c(1:10) / 10
  H2CH <- c(1:10) / 10
  for (h2ch in H2CH) {
    for (h2cd in H2CD) {
      print(paste("h2cd:", as.character(h2cd), sep = ""))
      print(paste("h2ch:", as.character(h2ch), sep = ""))
      seg_las <- crownsegmentr::segment_tree_crowns(point_cloud,
                                                    crown_diameter_to_tree_height = h2cd,
                                                    crown_height_to_tree_height = h2ch,
                                                    segment_crowns_only_above = 0)
      print('segmentation finished')
      print('filtering core area pts')
      las_df <-data.frame(X=seg_las$X, Y=seg_las$Y, Z=seg_las$Z, ID=seg_las$crown_id, confiScore=seg_las$confiScore)
      las_df$ID[is.na(las_df$ID)] <- 10000
      uni_ids <- unique(las_df$ID)
      Vx <- vector() 
      Vy <- vector() 
      Vz <- vector()
      Vid <- vector()
      Vconfi <- vector()
      for (id_i in uni_ids) {
        if (id_i == 0) {next}
        tmp_df <- las_df[which(las_df$ID == id_i),]
        tmp_x <- c(tmp_df$X)
        tmp_y <- c(tmp_df$Y)
        matrix_xy <- matrix(cbind(tmp_x, tmp_y), ncol = 2)
        sf_pts <- st_multipoint(matrix_xy)
        tree_hull = st_convex_hull(sf_pts)
        intersect_poly = st_intersection(tree_hull, boundary_poly)
        common_area_rate <- st_area(intersect_poly) / st_area(tree_hull)
        if (is.na(common_area_rate)){
          print("Common area is NaN")
        }
        else if (common_area_rate < 0.5){print('Insufficient Overlaps')}
        else{
          print(paste("overlapped area rate is:", as.character(common_area_rate)))
          Vx <- c(Vx, tmp_x)
          Vy <- c(Vy, tmp_y)
          Vz <- c(Vz, tmp_df$Z)
          Vid <- c(Vid, tmp_df$ID)
          Vconfi <- c(Vconfi, tmp_df$confi)
        }
      }
      feasible_pts <- data.frame(X = Vx, Y = Vy, Z = Vz, ID = Vid, confiScore=Vconfi)
      # exclude invalid points
      outdata = filter(feasible_pts, ID != 10000)
      out_name <- paste("sepilok_h2cd_", as.character(h2cd),
                        "_h2ch_", as.character(h2ch), ".h5", sep = "")
      # out_path <- paste(root_path, out_name, sep = "/")
      write.csv(outdata, out_path)
      print('                         ')
      print("------- One Loop Finished --------")
    }
  }
  print('Complete...')
}


#' Implement Dalponte2016 within parameter space
#' @name Dalponte2016
#' @param data_path character. path for point cloud data.
#' @param boundary_path character. path for core area boundary shapefile data.
#' @param out_path charcter. path for exporting segmentation point clouds of core area.
#' @param THSEED list. height threshold for including neighbouring pixel compared to treetop height.
#' @param THCR list. height threshold for including neighbouring pixel compared to average crown height.
dalponte2016 <- function(data_path, boundary_path, out_path){
  #data_path <- '/Volumes/T7/Data/New_Sepilok/ALS_xyzconfi.las'
  #boundary_path <- '/Volumes/T7/Data/New_Sepilok/Boundary_shp/concave_hull.shp'
  boundary <- sf::st_read(boundary_path)
  boundary_poly <- boundary$geometry
  ws_params <- 5 # c(5,10,15,20,25)
  res_i <- 0.5
  smoothing_size <- c(1) #, 3, 5, 7)
  th_crown <- c(1:10) / 10
  th_seed <- c(1:10) / 10
  max_crown <- 50
  for (smoothing_size_i in smoothing_size){
    print(paste("smoothing size is:", as.character(smoothing_size_i), sep = ""))
    for (th_cr_i in th_crown) {
      for (th_seed_i in th_seed) {
        # read data, plot data, show data details
        las_raw <- readLAS(data_path) #, select = "confiScore")
        # add values to ReturnNumber to avoid errors
        las_raw@data$ReturnNumber <- 1L
        # generate chm
        chm <- rasterize_canopy(las_raw, res=res_i, algorithm = pitfree(subcircle = 0.2), pkg="raster")
        # smoothing chm
        ker <- matrix(1,smoothing_size_i,smoothing_size_i)
        chm <- raster::focal(chm, w = ker, fun = mean, na.rm = TRUE)
        # extract treetops
        ttops <- lidR::locate_trees(chm, lmf(ws = ws_params, hmin=0, shape='circular'))
        # Dalponte2016 segmentation
        system.time(seg_las <- segment_trees(las_raw, dalponte2016(chm = chm, treetops = ttops,
                                                                   th_tree = 0,
                                                                   th_seed = th_seed_i,
                                                                   th_cr = th_cr_i,
                                                                   max_cr = max_crown)))
        out_path <- paste(root_path, 'test.las', sep = "/")
        # lidR::writeLAS(seg_las, out_path)
        print("segmentation complete!")
        # filtering core area point clouds
        las_df <-data.frame(X=seg_las$X, Y=seg_las$Y, Z=seg_las$Z, ID=seg_las$treeID, confiScore=seg_las$confiScore)
        las_df$ID[is.na(las_df$ID)] <- 10000
        uni_ids <- unique(las_df$ID)
        Vx <- vector() 
        Vy <- vector() 
        Vz <- vector()
        Vid <- vector()
        Vconfi <- vector()
        for (id_i in uni_ids) {
          if (id_i == 0) {next}
          tmp_df <- las_df[which(las_df$ID == id_i),]
          tmp_x <- c(tmp_df$X)
          tmp_y <- c(tmp_df$Y)
          matrix_xy <- matrix(cbind(tmp_x, tmp_y), ncol = 2)
          sf_pts <- st_multipoint(matrix_xy)
          tree_hull = st_convex_hull(sf_pts)
          intersect_poly = st_intersection(tree_hull, boundary_poly)
          common_area_rate <- st_area(intersect_poly) / st_area(tree_hull)
          if (is.na(common_area_rate)){
            print("Common area is NaN")
          }
          else if (common_area_rate < 0.5){print('Insufficient Overlaps')}
          else{
            print(paste("overlapped area rate is:", as.character(common_area_rate)))
            Vx <- c(Vx, tmp_x)
            Vy <- c(Vy, tmp_y)
            Vz <- c(Vz, tmp_df$Z)
            Vid <- c(Vid, tmp_df$ID)
            Vconfi <- c(Vconfi, tmp_df$confi)
          }
          print('ok')
        }
        feasible_pts <- data.frame(X = Vx, Y = Vy, Z = Vz, ID = Vid, confiScore=Vconfi)
        # exclude invalid points
        outdata = filter(feasible_pts, ID != 10000)
        write.csv(outdata, outpath)
      }
    }
  }
  print("Finished...")
}


#' Implement Dalponte2016+ within parameter space
#' @name Dalponte2016plus
#' @param data_path character. path for point cloud data.
#' @param lut_path character. path for lookuptable.
#' @param boundary_path character. path for core area boundary shape-file data.
#' @param out_path character. path for exporting segmentation point clouds of core area.
#' @param THSEED list. same definition with THSEED in Dalponte2016.
#' @param THCR list. same definition with THCR in Dalponte2016.
dalponte2016plus <- function(data_path, lut_path, boundary_path, out_path){
  library(tidyverse)
  library(readxl)
  library(magrittr)
  # --- read point clouds --- #
  point_cloud <- readLAS(data_path)
  lasData <- point_cloud@data
  # --- read boundary shp --- #
  boundary <- sf::st_read(boundary_path)
  boundary_poly <- boundary$geometry
  # --- read lut data --- #
  lut <- data.frame(read.csv(lut_path)[-1])
  print(head(lut))
  # --- Define Parameter and the Range --- #
  THSEED <- c(1:10)/10
  THCR <- c(1:10)/10
  for (thseed in THSEED){
    for (thcr in THCR){
      print('Start Segmentation...')
      se<-itcLiDARallo(lasData$X,lasData$Y,lasData$Z,epsg=NULL,
                       lut= lut,
                       resolution = 0.5,
                       TRESHSeed = thseed,
                       TRESHCrown = thcr,
                       HeightThreshold = 0,
                       cw = 1)
      seg_las =  se[2][[1]]
      print('Segmentation Finished and Core Area Filtering...')
      if (!is.null(seg_las))
      {
        las_df <-data.frame(X=seg_las$X, Y=seg_las$Y, Z=seg_las$Z, ID=seg_las$ID, confiScore=lasData$confiScore)
        las_df$ID[is.na(las_df$ID)] <- 10000
        uni_ids <- unique(las_df$ID)
        Vx <- vector() 
        Vy <- vector() 
        Vz <- vector()
        Vid <- vector()
        Vconfi <- vector()
        for (id_i in uni_ids) {
          if (id_i == 0) {next}
          tmp_df <- las_df[which(las_df$ID == id_i),]
          tmp_x <- c(tmp_df$X)
          tmp_y <- c(tmp_df$Y)
          matrix_xy <- matrix(cbind(tmp_x, tmp_y), ncol = 2)
          sf_pts <- st_multipoint(matrix_xy)
          tree_hull = st_convex_hull(sf_pts)
          intersect_poly = st_intersection(tree_hull, boundary_poly)
          common_area_rate <- st_area(intersect_poly) / st_area(tree_hull)
          if (is.na(common_area_rate)){
            print("Common area is NaN")
          }
          else if (common_area_rate < 0.5){print('Insufficient Overlaps')}
          else{
            print(paste("overlapped area rate is:", as.character(common_area_rate)))
            Vx <- c(Vx, tmp_x)
            Vy <- c(Vy, tmp_y)
            Vz <- c(Vz, tmp_df$Z)
            Vid <- c(Vid, tmp_df$ID)
            Vconfi <- c(Vconfi, tmp_df$confi)
          }
          print('ok')
        }
        feasible_pts <- data.frame(X = Vx, Y = Vy, Z = Vz, ID = Vid, confiScore=Vconfi)
        # exclude invalid points
        tau_number <- substr(file, 24, 25)
        outdata = filter(feasible_pts, ID != 10000)
        outname <- paste("tau_", as.character(tau_number),"_THSEED_", as.character(thseed),
                         "_THCR_", as.character(thcr),"_cw_1.csv", sep = "")
        outpath = paste(outroot, outname, sep="/")
        write.csv(outdata, outpath)
        print('ok')
      }
      else{
        print('Segmentation Result is NULL, Directly store a NULL file')
        las_df <- data.frame(X=NULL, Y=NULL, Z=NULL, ID=NULL, confiScore=NULL)
        tau_number <- substr(file, 24, 25)
        outname <- paste("tau_", as.character(tau_number),"_THSEED_", as.character(thseed),
                         "_THCR_", as.character(thcr),"_cw_1.csv", sep = "")
        outpath = paste(outroot, outname, sep="/")
        write.csv(las_df, out_path)
        print('One Loop Finished...')
      }
    }
  }
  print('Complete...')
}


#' Implement Li2012 within parameter space
#' @name Li2012
#' @param data_path character. path for point cloud data.
#' @param boundary_path character. path for core area boundary shape-file data.
#' @param out_path character. path for exporting segmentation point clouds of core area.
#' @param DT1 list. 
#' @param DT2 list.
li2012 <- function(data_path,boundary_path, out_path){
  boundary <- sf::st_read(boundary_path)
  boundary_poly <- boundary$geometry
  point_cloud <- readLAS(data_path) # , select='xyz')
  # plot(point_cloud)
  R = c(1)
  dt1 = c(1:10)
  dt2 = c(1:10)
  for (r_i in R) {
    for (dt1_i in dt1) {
      print(paste("input dt1 is:", as.character(dt1_i), sep = ""))
      for (dt2_i in dt2) {
        print(paste("input dt2 is:", as.character(dt2_i), sep = ""))
        outname <- paste('sepilok_', 'R_',as.character(r_i), 
                         '_dt1_', as.character(dt1_i), '_dt2_', as.character(dt2_i), '.h5', sep="")
        # Execute li2012 method
        seg_las = lidR::segment_trees(point_cloud, li2012(dt1=dt1_i, dt2=dt2_i, R=r_i, Zu=15, hmin=2, speed_up=12))
        # filtering core area pts
        las_df <-data.frame(X=seg_las$X, Y=seg_las$Y, Z=seg_las$Z, ID=seg_las$treeID, confiScore=seg_las$confiScore)
        las_df$ID[is.na(las_df$ID)] <- 10000
        uni_ids <- unique(las_df$ID)
        Vx <- vector() 
        Vy <- vector() 
        Vz <- vector()
        Vid <- vector()
        Vconfi <- vector()
        for (id_i in uni_ids) {
          if (id_i == 0) {next}
          tmp_df <- las_df[which(las_df$ID == id_i),]
          tmp_x <- c(tmp_df$X)
          tmp_y <- c(tmp_df$Y)
          matrix_xy <- matrix(cbind(tmp_x, tmp_y), ncol = 2)
          sf_pts <- st_multipoint(matrix_xy)
          tree_hull = st_convex_hull(sf_pts)
          intersect_poly = st_intersection(tree_hull, boundary_poly)
          common_area_rate <- st_area(intersect_poly) / st_area(tree_hull)
          if (is.na(common_area_rate)){
            print("Common area is NaN")
          }
          else if (common_area_rate < 0.5){print('Insufficient Overlaps')}
          else{
            print(paste("overlapped area rate is:", as.character(common_area_rate)))
            Vx <- c(Vx, tmp_x)
            Vy <- c(Vy, tmp_y)
            Vz <- c(Vz, tmp_df$Z)
            Vid <- c(Vid, tmp_df$ID)
            Vconfi <- c(Vconfi, tmp_df$confi)
          }
        }
        feasible_pts <- data.frame(X = Vx, Y = Vy, Z = Vz, ID = Vid, confiScore=Vconfi)
        # exclude invalid points
        outdata = filter(feasible_pts, ID != 10000)
        write.csv(outdata, outpath)
        print('One Loop Finished...')
      }
    }
  }
  print('----- Complete -----')
}
