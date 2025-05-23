from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, ConversationalChatAgent, Tool
from langchain_openai import ChatOpenAI
from langchain.utilities import SerpAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from env_config import OPENAI_API_MODEL, OPENAI_API_TEMPERATURE, SERPAPI_API_KEY

def init_agent_chain(memory):
    # 1) LLM
    llm = ChatOpenAI(
        model_name=OPENAI_API_MODEL,
        temperature=OPENAI_API_TEMPERATURE,
        streaming=True,
    )

    # 2) 검색 도구
    duck = DuckDuckGoSearchRun(name="DuckDuckGo")
    serp = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)
    def search_fallback(q: str) -> str:
        try: return duck.run(q)
        except: return serp.run(q)
    search_tool = Tool.from_function(
        func=search_fallback,
        name="WebSearch",
        description="반려견 관련 정보를 검색할 때 사용합니다. (DuckDuckGo→Fallback Google)",
    )

    # 3) 전문 상담사 페르소나
    system_prompt = SystemMessagePromptTemplate.from_template(
        "당신은 10년 경력의 수의사이자 반려견 행동 전문가입니다. "
        "모든 반려견 관련 질문에 근거 기반으로, "
        "친절하고 이해하기 쉽게 한국어로 답변하세요."
    )

    # 4) 대화 프롬프트 조합
    prompt = ChatPromptTemplate.from_messages([
        system_prompt,
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ])

    # 5) 에이전트 생성
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
