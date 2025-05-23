# 환경변수 로드
from dotenv import load_dotenv
import os

# 환경변수 불러오기
load_dotenv()

# 환경 변수 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL")
OPENAI_API_TEMPERATURE = os.getenv("OPENAI_API_TEMPERATURE")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

COOKIE_SECRET=os.getenv("COOKIE_SECRET")
SERPAPI_API_KEY=os.getenv("SERPAPI_API_KEY")
PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
