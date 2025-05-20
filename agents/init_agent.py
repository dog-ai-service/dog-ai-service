from langchain.agents import AgentExecutor,ConversationalChatAgent
from langchain_openai import ChatOpenAI
from env_config import OPENAI_API_MODEL, OPENAI_API_TEMPERATURE
from langchain_community.tools import DuckDuckGoSearchRun

# 랭체인-에이전트 초기화
def init_agent_chain(memory):
    llm = ChatOpenAI(model_name  = OPENAI_API_MODEL, temperature = OPENAI_API_TEMPERATURE, streaming = True)
    tools = [DuckDuckGoSearchRun(name="Search")]
    chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
    return AgentExecutor.from_agent_and_tools(agent=chat_agent, tools=tools, memory=memory, return_intermediate_steps=True, handle_parsing_errors=True)
