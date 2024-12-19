import pandas as pd
import numpy as np
import pickle
from AniML_utils_PoseFeatureExtraction import *
from AniML_utils_PixBrightnessFeatureExtraction import *
from ARBEL_utils_Filter import *


"""
ARBEL Feature Extraction and Prediction Pipeline

This script contains two primary functions to support the ARBEL (Automated Recognition of Behavioral Events in Lab animals) analysis workflow:

1. **ARBEL_ExtractFeatures**: 
   - Extracts pose-estimation-based features and pixel brightness features from video and pose data.
   - Combines these features into a single feature matrix for further analysis.
   - Optionally saves the feature matrix for reuse.

2. **ARBEL_Predict**:
   - Loads a trained classifier model to predict behaviors based on the extracted features.
   - Applies a threshold to the prediction probabilities to generate binary behavior labels.
   - Optionally applies a filtering step to refine predictions based on predefined criteria (e.g., minimum bout length).

   Parameters:
   - `clf_model_path`: Path to the trained classifier model.
   - `X`: Feature matrix generated by `ARBEL_ExtractFeatures`.
   - Additional parameters allow customization of prediction thresholds and filtering settings.

Dependencies:
- The script uses helper functions from the following custom modules:
  - `AniML_utils_PoseFeatureExtraction`
  - `AniML_utils_PixBrightnessFeatureExtraction`
  - `ARBEL_Filter`
"""

def ARBEL_ExtractFeatures(pose_data_file,
                          video_file_path,
                          bp_pixbrt_list,
                          dt_vel=2,
                          square_size=40,
                          pix_threshold=0.3,
                          min_prob=0.8,
                          scale_x=1,
                          scale_y=1,
                          Flip=False,
                          Filter=False,
                          BPprob_thresh=0.8,
                          bp_include_list=None,
                          create_video=False,
                          save_feature_mat=False):
    """
    Extracts pose-based and pixel brightness-based features from pose estimation data and video files.

    Parameters:
        pose_data_file (str): Path to the pose estimation data file (.h5 or .csv).
        video_file_path (str): Path to the video file corresponding to the pose data.
        bp_pixbrt_list (list): List of body parts to analyze.
        dt_vel (int): Time step for calculating velocities (default=2).
        square_size (int): Size of the square (in pixels) for brightness extraction (default=40).
        pix_threshold (float): Threshold for pixel brightness analysis (default=0.3).
        min_prob (float): Minimum probability for valid body parts in brightness extraction (default=0.8).
        scale_x (float): Scaling factor for x-coordinates (default=1).
        scale_y (float): Scaling factor for y-coordinates (default=1).
        Flip (bool): Whether to flip the video and pose data (default=False).
        Filter (bool): Whether to apply filtering to pose data (default=False).
        BPprob_thresh (float): Minimum probability threshold for pose data (default=0.8).
        bp_include_list (list): Specific body parts to include in pose features; None uses all body parts (default=None).
        create_video (bool): Whether to create a labeled video for output (default=False).
        save_feature_mat (bool): If True, saves the extracted features as a .h5 file (default=False).
        n_jobs (int): Number of CPU cores to use for processing (default=1).

    Returns:
        pd.DataFrame: A dataframe containing the extracted features.
    """
    # Extract pose-based features
    PoseFeatures = PoseFeatureExtract(data_file=pose_data_file,
                                      dt_vel=dt_vel,
                                      x_scale=scale_x,
                                      y_scale=scale_y,
                                      Flip=Flip,
                                      Filter=Filter,
                                      BPprob_thresh=BPprob_thresh,
                                      bp_include_list=bp_include_list)

    # Extract brightness-based features
    PixBrightFeatures = PixBrightFeatureExtract(pose_data_file=pose_data_file,
                                                video_file_path=video_file_path,
                                                bp_pixbrt_list=bp_pixbrt_list,
                                                square_size=square_size,
                                                pix_threshold=pix_threshold,
                                                dt_vel=dt_vel,
                                                scale_x=scale_x,
                                                scale_y=scale_y,
                                                create_video=create_video,
                                                min_prob=min_prob)

    # Combine pose and brightness features
    X = pd.concat([PoseFeatures, PixBrightFeatures], axis=1)
    print(f'Extracted features from: {pose_data_file}')

    # Save the feature matrix if requested
    if save_feature_mat:
        save_path = os.path.splitext(pose_data_file.split('DLC')[0])[0] + '_feature_mat.h5'
        with open(save_path, 'wb') as f:
            feature_matrix = {'X_test': X}
            pickle.dump(feature_matrix, f)
        print(f'Saved feature table to: {save_path}')

    return X

def ARBEL_Predict(clf_model_path, X, min_bout=3, min_after_bout=1, max_gap=0, best_thresh=[]):
    # Adjusting predictions

    with open(clf_model_path, 'rb') as f:
        loaded_model = pickle.load(f)
    clf_model = loaded_model['clf_model']
    # Behavior_type = loaded_model['Behavior_type']
    min_bout = loaded_model['min_bout']
    min_after_bout = loaded_model['min_after_bout']
    max_gap = loaded_model['max_gap']
    # dt_vel = loaded_model['dt_vel']
    # bp_pixbrt_list = loaded_model['bp_pixbrt_list']

    if best_thresh == []:
        best_thresh = loaded_model['best_thresh']

    y_pred_th = pd.DataFrame(clf_model.predict_proba(X[clf_model.feature_names_in_])[:, 1] >= best_thresh)
    y_pred_filt = ARBEL_Filter(y_pred_th, polish_repeat=2, min_bout=min_bout, min_after_bout=min_after_bout,
                                 max_gap=max_gap, min_after_gap=1)

    y_pred_filt = pd.DataFrame(y_pred_filt.iloc[:,0] + 0)
    y_pred_th = pd.DataFrame(y_pred_th.iloc[:, 0] + 0)
    return y_pred_filt, y_pred_th