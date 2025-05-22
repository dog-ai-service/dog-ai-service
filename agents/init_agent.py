from langchain.agents import AgentExecutor, ConversationalChatAgent, Tool
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.utilities import SerpAPIWrapper
from env_config import OPENAI_API_MODEL, OPENAI_API_TEMPERATURE, SERPAPI_API_KEY

def init_agent_chain(memory):
    llm = ChatOpenAI(model_name=OPENAI_API_MODEL, temperature=OPENAI_API_TEMPERATURE, streaming=True)

    # 1. DuckDuckGo
    duck = DuckDuckGoSearchRun(name="DuckDuckGo")

    # 2. SerpAPI (Google Search)
    serp = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)

    # 3. DuckDuckGo가 실패하면 SerpAPI(=Google)로 폴백하는 단일 Search 함수
    def search_fallback(query: str) -> str:
        try:
            return duck.run(query)
        except Exception:
            # DuckDuckGo 에러 시 SerpAPI로 재시도
            return serp.run(query)

    # 4. LangChain Tool로 래핑
    search_tool = Tool.from_function(
        func=search_fallback,
        name="Search",
        description=("웹에서 답을 찾아야 할 때 사용하세요. (DuckDuckGo실패 시 -> SerpAPI 폴백)"),
    )

    # 5. 한국어 고정 system prompt
    system_prompt = SystemMessagePromptTemplate.from_template(
        "당신은 한국어로만 답변하는 AI 비서입니다. 절대로 영어로 답하지 마세요."
    )

    # 6. 대화 히스토리, 사용자 입력 placeholder
    human_prompt   = HumanMessagePromptTemplate.from_template("{input}")
    history_prompt = MessagesPlaceholder(variable_name="chat_history")

    # 7. PromptTemplate 조합
    prompt = ChatPromptTemplate.from_messages([
        system_prompt,
        history_prompt,
        human_prompt,
    ])

    chat_agent = ConversationalChatAgent.from_llm_and_tools(
        llm=llm,
        tools=[search_tool],
        prompt=prompt,
    )

    return AgentExecutor.from_agent_and_tools(
        agent=chat_agent,
        tools=[search_tool],
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )
