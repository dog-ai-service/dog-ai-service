# 랭체인 에이전트
# AgentExecutor : 에이전트, 툴, 메모리 모두 결합
# load_tools : 위키피디아, 검색엔등등 연결
# create_openai_tools_agent : openai를 위한 에이전트 (메모리, 툴, 모델)
from langchain.agents import AgentExecutor, load_tools, create_openai_tools_agent
# 대화 내용을 기반으로 gpt가 응답을 할수 있게 제공
from langchain.memory import ConversationBufferMemory
# 랭체인 + openai 관련 로드
from langchain_openai import ChatOpenAI
# 허브
from langchain import hub
# 환경변수
from env_config import OPENAI_API_MODEL, OPENAI_API_TEMPERATURE

# 랭체인-에이전트 초기화
def init_agent_chain(history):
    # 1. GPT 생성
    llm = ChatOpenAI(
        model_name=OPENAI_API_MODEL,
        temperature=OPENAI_API_TEMPERATURE
    )
    # 2. 툴 생성 (hub를 통해서 외부 자원 활용 -> 검색증강, 데이터 추가 등등....)
    tools = load_tools([  # "ddg-search",
        "wikipedia"])
    # 3. 외부 자원을 사용할 수 있는 허브 구성
    hub_tool = hub.pull('hwchase17/openai-tools-agent')
    # 4. (*)메모리 구성 (채팅 대화 기록을 기반으로 응답할수 있게 구성)
    memory = ConversationBufferMemory(
        chat_memory=history,
        # 이 대화에 대해 특정할수 있는 키, 현재는 고정, 차후 대화별로 다르게 구성 가능함
        # chatgpt 에서 왼쪽 메뉴에 대화창 별로 관리되는 항목 체크
        memory_key='my_first_chat',
        return_messages=True
    )
    agent = create_openai_tools_agent(llm, tools, hub_tool)
    return AgentExecutor(agent=agent, tools=tools, memory=memory)

