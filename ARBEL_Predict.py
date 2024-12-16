import pandas as pd
import numpy as np
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

import pickle
from AniML_utils_PoseFeatureExtraction import *
from AniML_utils_PixBrightnessFeatureExtraction import *
from ARBEL_Filter import *

def ARBEL_ExtractFeatures(pose_data_file,
                video_file_path,
                bp_list,
                dt_before=1, dt_after=1,
                square_size = 44, pix_threshold = 100,
                create_video = False, Flip=False, save_feature_mat=0,n_jobs=1, bp_include_list=None):

    PoseFeatures = PoseFeatureExtract(pose_data_file, dt_before, Flip)
    # vid_file = os.path.basename(pose_data_file).split("DLC", 1)[0] + '.avi'
    LumFeatures = PixBrightFeatureExtract(pose_data_file=pose_data_file, video_file_path=video_file_path,
                                          bp_list=bp_list, square_size=square_size, pix_threshold=pix_threshold,
                                          Flip=Flip, create_video=False, n_jobs=n_jobs)
    X = pd.concat([PoseFeatures, LumFeatures], axis=1)
    print(f'Extracted features from: {pose_data_file}')
    if save_feature_mat:
        with open(pose_data_file.split('DLC')[0] + '_feature_mat.h5', 'wb') as f:
            feature_matrix={'X_test': X}
            pickle.dump(feature_matrix, f)
        print(f'Saved feature table to: {pose_data_file.split("DLC")[0]}_feature_mat.h5')
    return X

def ARBEL_Predict(clf_model_path, X, min_bout=3, min_after_bout=1, max_gap=0, best_thresh=[]):
    # Adjusting predictions

    with open(clf_model_path, 'rb') as f:
        loaded_model = pickle.load(f)
    clf_model = loaded_model['clf_model']
    Behavior_type = loaded_model['Behavior_type']
    min_bout = loaded_model['min_bout']
    min_after_bout = loaded_model['min_after_bout']
    max_gap = loaded_model['max_gap']
    dt_vel = loaded_model['dt_vel']
    bp_list = loaded_model['bp_pixbrt_list']

    if best_thresh == []:
        best_thresh = loaded_model['best_thresh']

    y_pred_th = pd.DataFrame(clf_model.predict_proba(X[clf_model.feature_names_in_])[:, 1] >= best_thresh)
    y_pred_filt = ARBEL_Filter(y_pred_th, polish_repeat=2, min_bout=min_bout, min_after_bout=min_after_bout,
                                 max_gap=max_gap, min_after_gap=1)

    y_pred_filt = pd.DataFrame(y_pred_filt.iloc[:,0] + 0)
    y_pred_th = pd.DataFrame(y_pred_th.iloc[:, 0] + 0)
    return y_pred_filt, y_pred_th