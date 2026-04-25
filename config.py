import os


class Config:
    """
    Central Configuration for the Iot maintenance System
    """

    # Directory paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'Data')
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')

    # File Paths
    CSV_PATH = os.path.join(DATA_DIR, 'industrial_fault_detection.csv')
    DB_PATH = os.path.join(DATA_DIR, 'iot_maintenance.db')

    # Model Path
    RF_MODEL_PATH = os.path.join(MODEL_DIR, 'random_forest_model.pkl')
    ISO_MODEL_PATH = os.path.join(MODEL_DIR, 'isolation_forest_model.pkl')
    SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')

    # Feature columns
    FEATURE_COLUMNS = ['vibration', 'temperature', 'pressure', 'rms_vibration', 'mean_temp']

    # Model hyperparameters

    RF_PARAMS = {
        'n_estimators': 100,
        'max_depth': 15,
        'min_samples_split': 5,
        'random_state': 42,
        'class_weight': 'balanced',
        'n_jobs': -1
    }

    ISO_FOREST_PARAMS = {
        'contamination': 0.1,
        'random_state': 42,
        'n_estimator': 100,
        'n_jobs': -1
    }

    # Training Parameters
    TEST_SIZE = 0.2
    RANDOM_STATE = 42

    # Health score threshold
    HEALTH_THRESHOLD = {
        'low_risk': 80,
        'medium_risk': 60,
        'high_risk': 40
    }

    # Column mapping for CVS
    COLUMN_MAPPING = {
        'Timestamp': 'timestamp',
        'Vibration (mm/s)': 'vibration',
        'Temperature (Degree)': 'temperature',
        'Pressure (bar)': 'pressure',
        'RMS Vibration': 'rms_vibration',
        'Faulty Label': 'fault_label'
    }

    @classmethod
    def create_directories(cls):
        """
        create necessary directories if they don't exist
        :return:
        """
        for director in [cls.DATA_DIR, cls.MODEL_DIR, cls.LOGS_DIR]:
            os.makedirs(director, exist_ok=True)
