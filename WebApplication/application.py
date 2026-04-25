# Author SnehalNakhawa
# Date: 1st April
# Description : Its web application module to display the prediction and anomaly detection
import streamlit as st

from WebUtility import showDashboard, showAnalytics, show_prediction, showAlerts, showAIAgent
from applicationUtility import ApplicationUtility, load_models

# Set page config
st.set_page_config(
    page_title="IoT Predictive Maintenance Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = '../data/iot_maintenance.db'

rf_model, iso_forest, scaler = load_models()


# STREAMLIT UI

def main():
    # Header
    st.title("🏭 Industrial IoT Predictive Maintenance Dashboard")
    st.markdown("AI-Powered Machine Health Monitoring & Failure Prediction")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")

        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "🔮 Real-Time Prediction", "📈 Analytics", "⚠️ Alerts", "🤖 AI Agent"]
        )
        st.write(repr(page))
        st.markdown("---")

        # Machine selector
        st.subheader("Machine Filter")
        machine_id = st.selectbox("Select Machine", ["All Machines", "MACHINE_001", "MACHINE_002", "MACHINE_003"])

        st.markdown("---")

        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")
        st.info("💡 Tip: Run training script first if you see errors")

    # PAGE: DASHBOARD

    if page == "📊 Dashboard":
        showDashboard()

    # PAGE: REAL-TIME PREDICTION
    elif page == "🔮 Real-Time Prediction":

        show_prediction()

    # PAGE: ANALYTICS
    elif page == "📈 Analytics":
        showAnalytics()

    # PAGE: ALERTS
    elif page == "⚠️ Alerts":
        showAlerts()
    # PAGE: AI AGENT

    elif page == "🤖 AI Agent":
        showAIAgent()


if __name__ == "__main__":
    main()
