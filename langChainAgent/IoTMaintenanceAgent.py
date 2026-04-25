from langchain_ollama import ChatOllama
from langchain.agents import Tool, AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from langChainAgent.LangChainFunctions import LangChainFunctions


class IoTMaintenanceAgent:
    """
    LangChain agent with Ollama integration for IoT predictive maintenance
    """

    def __init__(self):
        """Initialize the agent with Ollama"""

        print("Initializing Ollama LLM (Mistral)...")
        self.llm = ChatOllama(
            model="mistral",
            temperature=0.5,
        )

        print("Setting up tools...")
        self.tools = [
            Tool(
                name="GetHealthStatus",
                func=LangChainFunctions.get_health_status,
                description="Get the current overall health status of all machines. Use this to answer questions about general machine health."
            ),
            Tool(
                name="GetHighRiskMachine",
                func=LangChainFunctions.get_high_risk_machine,
                description="Get a list of machines that are at high risk or critical status. Use this when asked about risky or problematic machines."
            ),
            Tool(
                name="GetAnomalyReport",
                func=LangChainFunctions.get_anomaly_report,
                description="Get recently detected anomalies and abnormal sensor readings. Use this for questions about unusual behavior."
            ),
            Tool(
                name="PredictMaintenance",
                func=LangChainFunctions.predict_maintenance_needs,
                description="Predict which machines need maintenance based on health trends. Use this for maintenance planning questions."
            ),
            Tool(
                name="GetSensorTrends",
                func=LangChainFunctions.get_sensor_trends,
                description="Get sensor reading trends (temperature, vibration, pressure) for analysis. Use this for sensor-related questions."
            )
        ]

        print("Creating agent with Ollama...")
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an IoT maintenance assistant. Analyze machine health data and provide clear, actionable insights.

Use the available tools to answer questions. Always use at least one tool to gather data before responding.

When answering:
1. Use the appropriate tool(s) to gather data
2. Analyze the results
3. Provide clear, concise recommendations"""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # Create agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)

        # Create executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

        print("Agent initialized successfully with Ollama!")

    def query(self, question: str) -> str:
        """Query the agent with a question"""
        try:
            response = self.agent_executor.invoke({"input": question})
            return response.get('output', str(response))
        except Exception as e:
            return f"Error processing query: {str(e)}"

    def reset_memory(self):
        """Reset conversation memory"""
        pass


def main():
    """Example usage"""
    print("=" * 80)
    print("IoT Maintenance Agent System with Ollama")
    print("=" * 80)

    try:
        agent = IoTMaintenanceAgent()
    except Exception as e:
        print(f"Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return

    queries = [
        "What is the current health status of all machines?",
        "Which machines need maintenance?",
        "Are there any recent anomalies?",
        "Show me the sensor trends for today"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 80}")
        print(f"QUERY {i}: {query}")
        print('=' * 80)

        response = agent.query(query)
        print(f"\nANSWER:\n{response}\n")


if __name__ == "__main__":
    main()
