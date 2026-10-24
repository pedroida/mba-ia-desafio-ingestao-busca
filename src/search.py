import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

prompt = PromptTemplate(
    input_variables=["contexto", "pergunta"],
    template=PROMPT_TEMPLATE,
)

def build_store():
    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL", "text-embedding-3-small"))
    return PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PGVECTOR_COLLECTION", "gpt5_collection"),
        connection=os.getenv("PGVECTOR_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag"),
        use_jsonb=True,
    )

def retrieve_context(store, inputs):
    results = store.similarity_search_with_score(inputs["pergunta"], k=10)
    return "\n\n".join(doc.page_content.strip() for doc, _score in results)

def search_prompt(question=None):
    try:
        store = build_store()
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-5-nano"),
            temperature=0,
            verbose=True,
        )
        chain = (
            RunnablePassthrough.assign(
                contexto=RunnableLambda(lambda inputs: retrieve_context(store, inputs))
            )
            | prompt
            | llm
            | StrOutputParser()
        )
    except Exception as error:
        print(f"Erro ao iniciar a busca: {error}")
        return None

    if question is None:
        return chain

    return chain.invoke({"pergunta": question})
