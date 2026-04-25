Industrial IoT Simulation

Overview
This project is an IoT based predictive Maintenance System that
-create and load sensor data into database
-train machine learning models
-Runs a Streamlit web application for prediction
https://github.com/nakhawasnehal7/IndustrialIoTSimulation
1. 
Create database script
   Run database scripts to create and insert data
   python create_database.py
   This will create required table
2.
Train machine learning model on the datasets
python Train_only.py
it generates the .pkl model files

3.
The web application displays the data and the predictions
Run the web application using command: streamlit run application.py

