import pandas as pd
import streamlit as st


import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from applicationUtility import ApplicationUtility, load_models
from agentModule import run_agent_query, is_agent_available, get_agent_status
from PredictionFunction import PredictionFunction

from applicationUtility import ApplicationUtility, load_models
def show_prediction():
    st.header("Real-Time Machine Health Prediction")

    st.markdown("""
    Enter current sensor readings to get instant machine health prediction.
    """)
    st.header("Real-Time Machine Health Prediction")
    col1, col2 = st.columns(2)

    with col1:
        vibration = st.number_input("Vibration (mm/s)", min_value=0.0, max_value=2.0, value=0.5, step=0.01)
        temperature = st.number_input("Temperature (°C)", min_value=0.0, max_value=200.0, value=85.0, step=1.0)
        pressure = st.number_input("Pressure (bar)", min_value=0.0, max_value=15.0, value=8.0, step=0.1)

    with col2:
        rms_vibration = st.number_input("RMS Vibration", min_value=0.0, max_value=2.0, value=0.6, step=0.01)
        mean_temp = st.number_input("Mean Temperature (°C)", min_value=0.0, max_value=200.0, value=90.0, step=1.0)
        machine_id_pred = st.text_input("Machine ID", value="MACHINE_001")

    if st.button("Predict Machine Health", type="primary"):
        with st.spinner("Analyzing sensor data..."):
            prediction = PredictionFunction.make_prediction(vibration, temperature, pressure, rms_vibration,
                                                            mean_temp)

            if prediction:
                st.success("Prediction Complete!")

                # Display results
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Health Score",
                        f"{prediction['health_score']:.1f}/100"
                    )

                with col2:
                    risk_color = {
                        'Low Risk': '🟢',
                        'Medium Risk': '🟡',
                        'High Risk': '🟠',
                        'Critical Risk': '🔴'
                    }
                    st.metric(
                        "Risk Level",
                        f"{risk_color.get(prediction['risk_classification'], '⚪')} {prediction['risk_classification']}"
                    )

                with col3:
                    st.metric(
                        "Fault Prediction",
                        prediction['fault_label']
                    )

                # Detailed analysis
                st.subheader("Detailed Analysis")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Fault Probabilities:**")
                    st.write(f"- Normal: {prediction['fault_probability']['normal']:.1%}")
                    st.write(f"- Fault: {prediction['fault_probability']['fault']:.1%}")
                    st.write(f"- Critical: {prediction['fault_probability']['critical']:.1%}")

                with col2:
                    st.write("**Anomaly Detection:**")
                    if prediction['is_anomaly']:
                        st.error(f" Anomaly Detected (Score: {prediction['anomaly_score']:.3f})")
                    else:
                        st.success(f"Normal Operation (Score: {prediction['anomaly_score']:.3f})")

                # Recommendations
                st.subheader("Recommendations")
                if prediction['health_score'] < 40:
                    st.error(
                        "🚨 **URGENT ACTION REQUIRED**: Schedule immediate maintenance. Machine is in critical condition.")
                elif prediction['health_score'] < 60:
                    st.warning(
                        "⚠️ **Schedule Maintenance**: Machine health is declining. Plan maintenance within the next few days.")
                elif prediction['health_score'] < 80:
                    st.info(
                        "ℹ️ **Monitor Closely**: Machine is operating below optimal conditions. Increase monitoring frequency.")
                else:
                    st.success("✅ **Normal Operation**: Machine is healthy. Continue regular monitoring.")

                # Save to database
                if st.button("💾 Save Prediction to Database"):
                    sensor_data = {
                        'vibration': vibration,
                        'temperature': temperature,
                        'pressure': pressure,
                        'rms_vibration': rms_vibration,
                        'mean_temp': mean_temp
                    }
                    if PredictionFunction.save_prediction_to_db(sensor_data, prediction, machine_id_pred):
                        st.success("Prediction saved to database!")
                        st.cache_data.clear()
                    else:
                        st.error(" Failed to save prediction to database")
            else:
                st.error(" Error making prediction. Please check if models are loaded correctly.")


def showDashboard():
    st.header("📊 Machine Health Dashboard")

    # Load data
    summary = ApplicationUtility.get_machine_health_summary()
    predictions_df = ApplicationUtility.load_predictions(100)
    risk_dist = ApplicationUtility.get_risk_distribution()

    if summary is not None and summary['total_predictions'] > 0:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Average Health Score",
                f"{summary['avg_health']:.1f}/100"
            )

        with col2:
            st.metric(
                "Predictions (24h)",
                int(summary['total_predictions'])
            )

        with col3:
            st.metric(
                "Anomalies Detected",
                int(summary['anomaly_count']),
                delta=f"-{int(summary['anomaly_count'])}" if summary['anomaly_count'] > 0 else "0",
                delta_color="inverse"
            )

        with col4:
            st.metric(
                "Faults Detected",
                int(summary['fault_count']),
                delta=f"-{int(summary['fault_count'])}" if summary['fault_count'] > 0 else "0",
                delta_color="inverse"
            )

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Risk Distribution")
            if not risk_dist.empty:
                fig = px.pie(
                    risk_dist,
                    values='count',
                    names='risk_classification',
                    color='risk_classification',
                    color_discrete_map={
                        'Low Risk': '#28a745',
                        'Medium Risk': '#ffc107',
                        'High Risk': '#fd7e14',
                        'Critical Risk': '#dc3545'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No risk data available")

        with col2:
            st.subheader("Health Score Trend")
            if not predictions_df.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=predictions_df['health_score'][:50],
                    mode='lines+markers',
                    name='Health Score',
                    line=dict(color='#007bff', width=2)
                ))
                fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Good")
                fig.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="Caution")
                fig.add_hline(y=40, line_dash="dash", line_color="red", annotation_text="Critical")
                fig.update_layout(
                    yaxis_title="Health Score",
                    xaxis_title="Recent Predictions",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No predictions available")

        # Recent predictions table
        st.subheader("Recent Predictions")
        if not predictions_df.empty:
            display_df = predictions_df[['timestamp', 'machine_id', 'health_score',
                                         'risk_classification', 'fault_prediction', 'is_anomaly']].head(10)
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No predictions available")
    else:
        st.warning("No prediction data available. Please run the training script first:")
        st.code("python complete_workflow.py", language="bash")


def showAnalytics():
    st.header("Advanced Analytics")

    sensor_df = ApplicationUtility.load_sensor_data(500)
    predictions_df = ApplicationUtility.load_predictions(500)

    if not sensor_df.empty:
        # Sensor correlations
        st.subheader("Sensor Correlations")

        numeric_cols = ['vibration', 'temperature', 'pressure', 'rms_vibration', 'mean_temp']
        corr_matrix = sensor_df[numeric_cols].corr()

        fig = px.imshow(
            corr_matrix,
            labels=dict(color="Correlation"),
            x=numeric_cols,
            y=numeric_cols,
            color_continuous_scale='RdBu_r',
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Sensor distributions by fault type
        st.subheader("Sensor Distributions by Fault Type")

        col1, col2 = st.columns(2)

        with col1:
            fig = px.box(
                sensor_df,
                x='fault_label',
                y='temperature',
                color='fault_label',
                title='Temperature Distribution by Fault Type'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.box(
                sensor_df,
                x='fault_label',
                y='vibration',
                color='fault_label',
                title='Vibration Distribution by Fault Type'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sensor data available for analytics")


def showAlerts():
    st.header("Maintenance Alerts")

    conn = ApplicationUtility.get_db_connection()
    if conn:
        alerts_df = pd.read_sql_query("""
                    SELECT * FROM maintenance_alerts 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                """, conn)
        conn.close()

        if not alerts_df.empty:
            st.dataframe(alerts_df, use_container_width=True)
        else:
            st.info("No alerts generated yet")

        # Create new alert
        st.subheader("Create Manual Alert")

        col1, col2 = st.columns(2)

        with col1:
            alert_machine = st.text_input("Machine ID", value="MACHINE_001")
            alert_type = st.selectbox("Alert Type", ["LOW_HEALTH_SCORE", "ANOMALY_DETECTED", "SENSOR_MALFUNCTION",
                                                     "SCHEDULED_MAINTENANCE"])

        with col2:
            alert_severity = st.selectbox("Severity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            alert_message = st.text_area("Message")

        if st.button("Create Alert"):
            conn = ApplicationUtility.get_db_connection()
            if conn:
                cursor = conn.cursor()

                cursor.execute('''
                            INSERT INTO maintenance_alerts 
                            (machine_id, alert_type, severity, message, timestamp)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                    alert_machine,
                    alert_type,
                    alert_severity,
                    alert_message,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))

                conn.commit()
                conn.close()

                st.success("Alert created successfully!")
                st.cache_data.clear()
                st.rerun()


def showAIAgent():
    st.header("🤖 AI Maintenance Agent")

    # Show warning if agent failed to load
    if not is_agent_available():
        status = get_agent_status()
        st.error(f"Agent unavailable: {status['error']}")
        st.code("ollama serve", language="bash")
        st.stop()

    st.markdown("Ask anything about your machines in plain English.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "agent_busy" not in st.session_state:
        st.session_state.agent_busy = False

    st.markdown("---")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state.agent_busy:
        prompt = st.chat_input("Type your question here...")
    else:
        prompt = None
        st.info("⏳ Agent is processing, please wait...")

    if prompt and not st.session_state.agent_busy:
        st.session_state.agent_busy = True

        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent thinking..."):
                response = run_agent_query(prompt)
            st.markdown(response)

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.session_state.agent_busy = False

    if st.session_state.chat_history:
        st.markdown("---")
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.agent_busy = False
            st.rerun()
