from langchain.agents import AgentExecutor, ConversationalChatAgent, Tool
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.utilities import SerpAPIWrapper  # or GoogleSearchAPIWrapper if you prefer
from env_config import OPENAI_API_MODEL, OPENAI_API_TEMPERATURE, SERPAPI_API_KEY

def init_agent_chain(memory):
    llm = ChatOpenAI(model_name=OPENAI_API_MODEL, temperature=OPENAI_API_TEMPERATURE, streaming=True)

    # ① 원래 DuckDuckGo 도구
    duck = DuckDuckGoSearchRun(name="DuckDuckGo")

    # ② SerpAPI (Google Search) 도구
    serp = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)

    # ③ 둘을 묶어, DuckDuckGo가 실패하면 SerpAPI(=Google)로 폴백하는 단일 Search 함수
    def search_fallback(query: str) -> str:
        try:
            return duck.run(query)
        except Exception:
            # DuckDuckGo 에러 시 SerpAPI로 재시도
            return serp.run(query)

    # ④ LangChain Tool로 래핑
    search_tool = Tool.from_function(
        func=search_fallback,
        name="Search",
        description=(
            "Use this to answer general queries by searching the web. "
            "First tries DuckDuckGo; if that fails, falls back to Google via SerpAPI."
        ),
    )

    tools = [search_tool]

    chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)

    return AgentExecutor.from_agent_and_tools(
        agent=chat_agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )
