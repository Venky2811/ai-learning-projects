from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# ============================================
# PART 1 - Define Tools
# ============================================

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    weather_data = {
        "mumbai": "32°C, sunny and humid",
        "delhi": "28°C, partly cloudy",
        "bangalore": "24°C, pleasant",
        "chennai": "34°C, hot and sunny"
    }
    city_lower = city.lower()
    if city_lower in weather_data:
        return f"Weather in {city}: {weather_data[city_lower]}"
    return f"Weather data not available for {city}"

@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression)
        return f"Result of {expression} = {result}"
    except Exception as e:
        return f"Calculation error: {e}"

@tool
def get_ai_fact(topic: str) -> str:
    """Get an interesting fact about an AI topic like RAG, LangChain, agents or LLM."""
    facts = {
        "rag": "RAG combines retrieval with generative AI for accurate answers",
        "langchain": "LangChain was created in 2022 and has over 70,000 GitHub stars",
        "agents": "AI agents use tools and reasoning to complete complex tasks",
        "llm": "LLMs are trained on hundreds of billions of words"
    }
    topic_lower = topic.lower()
    for key in facts:
        if key in topic_lower:
            return facts[key]
    return f"No specific fact found for {topic}"

tools = [get_weather, calculate, get_ai_fact]

# ============================================
# PART 2 - Create Agent using LangGraph
# ============================================

# this one line creates a full ReAct agent!
agent = create_react_agent(llm, tools)

# ============================================
# PART 3 - Run the Agent
# ============================================

def run_agent(question):
    print(f"\nQuestion: {question}")
    print("-" * 40)
    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    # get the last message which is the final answer
    final_answer = result["messages"][-1].content
    print(f"Final Answer: {final_answer}")
    return final_answer

print("=" * 50)
print("TEST 1 - Weather Query:")
print("=" * 50)
run_agent("What is the weather in Mumbai?")

print("\n" + "=" * 50)
print("TEST 2 - Math Calculation:")
print("=" * 50)
run_agent("What is 15 multiplied by 24 plus 100?")

print("\n" + "=" * 50)
print("TEST 3 - Multi Tool Query:")
print("=" * 50)
run_agent("What is the weather in Delhi and tell me a fact about RAG?")