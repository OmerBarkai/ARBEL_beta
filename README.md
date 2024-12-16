# ARBEL(beta) 
This repository contains tools for the beta version  of ARBEL (Automated Recognition of Behavioral Events in Lab animals). The following files are central to the workflow:

## **ARBEL_TrainClassifier.py**
This script trains a machine learning classifier to recognize specific behaviors in animals based on features extracted from pose estimation and video data. 

### Key Features:
- Prepares a feature matrix from pose-estimation data (DeepLabCut output) and corresponding videos.
- Integrates behavioral target labels (e.g., manually annotated behavior events) from `.csv` files.
- Trains a classification model using features and target labels.
- Saves the trained classifier model for later use in behavior prediction.
- Saves the model's performance metrics on the test set.
- Saves the feature importance explenation analysis (SHAP) figure.
Optional:
- Saves the learning curve 

### Input Requirements:
1. **Pose Estimation Data**: DLC `.h5` (or `.csv`) files should be in the `project/Videos` folder, alongside their corresponding video files.
2. **Video Files**: Should also reside in the `project/Videos` folder.
3. **Target Files**: Behavior labels in `.csv` format should be placed in the `project/Targets` folder.

---

## **ARBEL_AutoScore.py**
This script uses a trained classifier to automatically score behaviors in videos. It predicts behavior bouts and refines them with post-processing filters.

### Key Features:
- Loads a pre-trained ARBEL classifier model.
- Extracts features from pose estimation and video data using the same pipeline as in the training process.
- Predicts behaviors for each video based on the extracted features.
- Applies post-processing to refine predictions (e.g., removing spurious short bouts, filling small gaps).
- Generates output files with predicted behavior bouts.
Optional:
- Generates a video with frame-by-frame behavior bout labeling, indicating when a specific behavior occurs. 

### Input Requirements:
1. **Video Files**: Should reside in the `project/Videos` folder.
2. **Pose Estimation Data**: DLC `.h5` (or `.csv`) files should be in the `project/Videos` folder, alongside their corresponding video files. DLC pose-estimation can be also done as part of the pipeline. 
3. **Trained Classifier Model**: A model generated by `ARBEL_TrainClassifier.py`.

### Output:
- Predicted behavior bouts for each video are saved in the output folder.
- (Optional) Labeled behavior video is saved in the output folder.

---

## **Dependencies**
This project requires the following libraries and tools to run successfully:

### **Python Libraries**
1. **Core Libraries**
   - `os`: For file and directory operations.
   - `time`: For time-related operations.
   - `gc`: For garbage collection.
   - `random`: For random number generation.
   - `datetime`: For date and time management.
   - `glob`: For pattern matching file operations.

2. **Data Manipulation**
   - `pandas`: Data analysis and manipulation.
   - `numpy`: Numerical computing.

3. **Visualization**
   - `matplotlib`: For plotting and graphical visualization.
     - Requires a compatible backend (`Qt5Agg`) for interactive plotting.

4. **Computer Vision**
   - `cv2` (OpenCV): For video and image processing.

5. **Machine Learning**
   - `xgboost`: Gradient boosting framework for classification and regression tasks.
   - `sklearn` (scikit-learn): Tools for model evaluation, including:
     - `f1_score`, `precision_score`, `accuracy_score`, `recall_score`, `r2_score`
     - `confusion_matrix`, `ConfusionMatrixDisplay`
   - `shap`: SHAP (SHapley Additive exPlanations) for model explainability.

### **System Requirements**
- **Operating System**: Linux or Windows recommended (with compatible Python environment).
- **Video Backend**: Ensure OpenCV is installed and configured properly for video handling.
- GPU recommended. 
