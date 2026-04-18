# IoT Botnet Detection using Random Forest

## 📌 Project Overview
This project uses Machine Learning (Random Forest Classifier) to identify malicious botnet traffic within IoT networks. It processes large-scale network logs to distinguish between normal traffic and attack vectors.

## 📂 Folder Structure
- *MODELS/*: Saved .pkl files of the trained model.
- *DATASET/*: CSV files containing network traffic features.
- *RESULTS/*: Confusion matrix and accuracy graphs.
- *botnet_model.py*: The main Python script for training and evaluation.

## 🛠️ Requirements
- Python 3.x
- Scikit-learn
- Pandas / Numpy
- Matplotlib / Seaborn (for visualization)

## 🚀 How to Run
1. Ensure your dataset is in the DATASET/ folder.
2. Run the training script:
   ```bash
   python botnet_model.py