import time
import os
import glob
import uuid
import pdfplumber
import pinecone
import openai
from dotenv import load_dotenv
from tiktoken import encoding_for_model

load_dotenv()

# openai 생성
client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
# pinecone 생성
INDEX_NAME       = "dog-guidelines"
pc = pinecone.Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index_dbs = [idx.name for idx in pc.list_indexes()]

# 1) 인덱스 생성 (없으면)
if INDEX_NAME not in index_dbs:
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,            # text-embedding-ada-002 차원
        metric="cosine", 
        spec        = pinecone.ServerlessSpec('aws', 'us-east-1')
    )
    time.sleep(10) 
index = pc.Index(INDEX_NAME)

# 2) 토크나이저 세팅 (OpenAI 모델용)
enc = encoding_for_model("text-embedding-ada-002")
def count_tokens(text: str) -> int:
    return len(enc.encode(text))

# 3) PDF → 텍스트 추출 & 청크 분리
def extract_text_chunks(pdf_path, max_tokens=800):
    chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)
    # 단순히 문단 기준으로 분할해서, 토큰 수 초과 시 이어붙이기
    for para in full_text.split("\n\n"):
        if not para.strip():
            continue
        tokens = count_tokens(para)
        if tokens <= max_tokens:
            chunks.append(para)
        else:
            # 긴 문단은 문장 단위로 쪼개기
            temp = ""
            for sent in para.split(". "):
                if count_tokens(temp + sent) <= max_tokens:
                    temp += sent + ". "
                else:
                    chunks.append(temp.strip())
                    temp = sent + ". "
            if temp:
                chunks.append(temp.strip())
    return chunks

# 4) 임베딩 생성 & Pinecone 업서트
batch_size = 16
to_upsert = []

for pdf_file in glob.glob("vectordb/guidlines/*.pdf"):
    filename = os.path.basename(pdf_file)
    print(f"> Processing {filename}…")
    chunks = extract_text_chunks(pdf_file)
    for i, chunk in enumerate(chunks):
        # OpenAI embedding
        res = client.embeddings.create(
            model="text-embedding-ada-002",
            input=chunk
        )
        emb = res.data[0].embedding
        # Pinecone upsert용 메타
        meta = {
            "source": filename,
            "chunk_index": i
        }
        # 고유 ID
        uid = f"{filename}-{i}-{uuid.uuid4().hex[:8]}"
        to_upsert.append((uid, emb, meta))

        # 배치 업서트
        if len(to_upsert) >= batch_size:
            index.upsert(vectors=to_upsert)
            to_upsert = []

# 남은 업서트
if to_upsert:
    index.upsert(vectors=to_upsert)

print("✅ Pinecone ingestion complete!")
