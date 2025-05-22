import openai
import pinecone
from env_config import OPENAI_API_KEY,PINECONE_API_KEY

# from dotenv import load_dotenv
# import os
# load_dotenv()

INDEX_NAME       = "dog-guidelines"

# openai 생성
client = openai.OpenAI(api_key=OPENAI_API_KEY)
# client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# pinecone 생성
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
# pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(INDEX_NAME)

def summarize(text):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"You are a helpful assistant. Summarize the user-provided text in no more than three concise sentences."},
            {"role":"user","content": text}
        ],
        temperature=0.0
    )
    return resp.choices[0].message.content.strip()

def retrieve_guidelines(query: str, top_k: int = 3) -> list[str]:
    """
    1) query 문장을 embedding
    2) Pinecone에서 k개 청크 검색
    3) metadata['source']와 텍스트 청크 합쳐서 리턴
    """
    # 1) query embedding
    resp = client.embeddings.create(
        input=[query], 
        model='text-embedding-ada-002'
    )
    q_emb = resp.data[0].embedding

    # 2) 유사도 검색
    results = index.query(
        vector=q_emb,
        top_k=top_k,
        include_metadata=True,
        # namespace='default'
    )
    # 3) source + chunk 합치기
    contexts = []
    for match in results.matches:
        src = match.metadata["source"]
        chunk = match.metadata["chunk_text"]
        brief = summarize(chunk)
        contexts.append(f"[{src}] {brief}")
    return contexts

# rag_contexts = {
#             topic: "\n\n".join(retrieve_guidelines(topic, top_k=3))
#             for topic in ["feeding", "walking", "bathing", "grooming", "heartworm_prevention", "internal_parasite", "vaccination"]
#         }
# print(rag_contexts)