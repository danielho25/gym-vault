# cocoindex pipeline
import re
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from pgvector.psycopg import register_vector
from typing import Any
import cocoindex
import os
from numpy.typing import NDArray
import numpy as np
import time
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Pre-load stopwords to avoid threading issues
ENGLISH_STOPWORDS = set(stopwords.words('english'))


# cocoindex indexing flow
@cocoindex.op.function()
def extract_extension(filename: str) -> str:
    return os.path.splitext(filename)[1]  # get the extension only


def remove_html_tags(text: str) -> str:
    return re.sub(r"<.*?>", "", text)


# @cocoindex.op.function()
# def remove_whitespace(text: str) -> str:
#     return text.strip().replace(" ", "")


def convert_to_lower(text: str) -> str:
    return text.lower()


@cocoindex.transform_flow()
def code_to_embedding(text: cocoindex.DataSlice[str]) -> cocoindex.DataSlice[NDArray[np.float32]]:
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(
            model="sentence-transformers/all-MiniLM-L6-v2"
        ))


@cocoindex.flow_def(name="CodeEmbedding")
def code_embedding_flow(flow_builder: cocoindex.FlowBuilder, data_scope: cocoindex.DataScope):
    """
    Define an example flow that embeds files into database
    """
    data_scope["files"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(path="workout_forms",
                                    included_patterns=["*.py", "*.rs", "*.toml", "*.md", "*.json"],
                                    excluded_patterns=[".*", "target", "**/node_modules"]))

    code_embeddings = data_scope.add_collector()

    with data_scope["files"].row() as file:
        file["extension"] = file["filename"].transform(extract_extension)
        file["chunks"] = file["content"].transform(
            cocoindex.functions.SplitRecursively(),
            language=file["extension"],
            chunk_size=1000,
            chunk_overlap=300)

        with file["chunks"].row() as chunk:
            chunk["embedding"] = chunk["text"].call(code_to_embedding)
            code_embeddings.collect(filename=file["filename"], location=chunk["location"],
                                    code=chunk["text"], embedding=chunk["embedding"],
                                    start=chunk["start"], end=chunk["end"])

    code_embeddings.export(
        "code_embeddings",
        cocoindex.storages.Postgres(),
        primary_key_fields=["filename", "location"],
        vector_indexes=[
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
            )
        ],
    )


def search(pool: ConnectionPool, query: str, top_k=5) -> list[dict[str, Any]]:
    table_name = cocoindex.utils.get_target_default_name(code_embedding_flow,
                                                         "code_embeddings")

    # define the query_vector (embedded query) - this will also be normalized
    query_vector = code_to_embedding.eval(query)
    # run the query to get results
    with pool.connection() as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT filename, code, embedding <=> %s AS distance, start, "end"
                FROM {table_name} ORDER BY distance LIMIT %s
                """, (query_vector, top_k),
            )
            return [
                {
                    "filename": row[0],
                    "code": row[1],
                    "score": 1.0 - row[2],
                    "start": row[3],
                    "end": row[4]
                }
                for row in cur.fetchall()
            ]


def save_vector_results(results: list[dict[str, Any]], query: str) -> None:
    try:
        with open('vector_output.txt', 'w', encoding='utf-8') as f:
            f.write(f"cocoindex vector search results for query: {query} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            f.write("=" * 80 + "\n\n")

            if not results:
                f.write("No results found!")
                return

            for i, result in enumerate(results):
                f.write(f"Rank {i + 1} - Score: {result['score']: .4f}\n")
                f.write(f"File: {result['filename']} (L{result['start']['line']}-L{result['end']['line']})\n")
                f.write(f"Code: \n{result['code']}\n")
                f.write("-" * 80 + "\n\n")

            print(f"results added to vector_output.txt")

    except Exception as e:
        print(f"error saving results: {e}")


def _main() -> None:
    stats = code_embedding_flow.update()
    print(f"Updated Index: {stats}")

    # initialize db connection
    pool = ConnectionPool(os.getenv("COCOINDEX_DATABASE_URL"))

    # run some queries

    while True:
        query = input("Enter search query (or Enter or (q) to quit): ")  # Get user input
        if query == "" or query == 'q':
            break

        start_time = time.time()
        results = search(pool, query)
        end_time = time.time() - start_time

        print(f"Search completed in {end_time: .4f} seconds")
        print(f"found {len(results)} results")

        for i, result in enumerate(results):
            print(f"Rank {i + 1} - Score: {result['score']: .4f}")
            print(f"File: {result['filename']} (L{result['start']['line']}-L{result['end']['line']})")
            print(f"Code preview: {result['code'][:200]}...")
            print("-" * 80)

        save_vector_results(results, query)

        print("Search session ended.")


if __name__ == "__main__":
    load_dotenv()
    cocoindex.init()
    _main()
