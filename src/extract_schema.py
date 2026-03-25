"""Stage 3a: Schema-guided extraction into FalkorDB graph 'odyssey_schema'."""
import argparse
import sys
import yaml

from llama_index.core import PropertyGraphIndex
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.graph_stores.falkordb import FalkorDBGraphStore

sys.path.insert(0, "src")
from scrape import build_documents, load_config
from schema import EntityType, RelationType


def run(book: int, config: dict):
    llm = Ollama(model=config["ollama_model"], request_timeout=300)
    embed_model = OllamaEmbedding(model_name=config["ollama_model"])

    graph_store = FalkorDBGraphStore(
        url=f"redis://{config['falkordb_host']}:{config['falkordb_port']}",
        database="odyssey_schema",
    )

    # FalkorDB versions prior to 0.4.2 omit this attribute; set it explicitly
    if not hasattr(graph_store, "supports_vector_queries"):
        graph_store.supports_vector_queries = False

    kg_extractor = SchemaLLMPathExtractor(
        llm=llm,
        possible_entities=EntityType,
        possible_relations=RelationType,
        strict=True,
        max_triplets_per_chunk=config["max_triplets_schema"],
    )

    docs = build_documents(book, config)

    print(f"Running schema-guided extraction on {len(docs)} chunks...")
    index = PropertyGraphIndex.from_documents(
        docs,
        kg_extractors=[kg_extractor],
        property_graph_store=graph_store,
        embed_model=embed_model,
        show_progress=True,
    )
    print("Done. Graph stored in FalkorDB as 'odyssey_schema'.")
    return index


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", type=int, default=1)
    args = parser.parse_args()

    config = load_config()
    run(args.book, config)
