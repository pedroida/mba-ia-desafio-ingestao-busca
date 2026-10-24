import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector
from sqlalchemy import func, select

load_dotenv()

current_dir = Path(__file__).parent.parent
pdf_path = current_dir / "document.pdf"

def is_pdf_uploaded_to_database(store: PGVector, pdf_path: Path) -> bool:
    print("Checking if PDF is uploaded to database")
    source = str(pdf_path)
    with store._make_sync_session() as session:
        collection = store.get_collection(session)
        if not collection:
            return False

        uploaded_chunks = session.execute(
            select(func.count())
            .select_from(store.EmbeddingStore)
            .where(store.EmbeddingStore.collection_id == collection.uuid)
            .where(store.EmbeddingStore.cmetadata["source"].astext == source)
        ).scalar_one()

    return uploaded_chunks > 0

def ingest_pdf():
    print("Ingesting PDF")
    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL", "text-embedding-3-small"))

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PGVECTOR_COLLECTION", "gpt5_collection"),
        connection=os.getenv("PGVECTOR_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag"),
        use_jsonb=True,
    )

    if is_pdf_uploaded_to_database(store, pdf_path):
        print("PDF already uploaded")
        return

    print("PDF not uploaded, loading and splitting")
    docs = PyPDFLoader(str(pdf_path)).load()

    splits = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=False,
    ).split_documents(docs)

    if not splits:
        raise SystemExit(0)

    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in splits
    ]

    ids = [f"doc-{i}" for i in range(len(enriched))]
    print(f"Adding {len(enriched)} documents to database")
    store.add_documents(documents=enriched, ids=ids)
    print("PDF uploaded to database")


if __name__ == "__main__":
    ingest_pdf()