"""Stage 3b: Open-domain extraction into FalkorDB graph 'odyssey_open'."""
import argparse
import sys
import yaml

from llama_index.core import PropertyGraphIndex
from llama_index.core.indices.property_graph import DynamicLLMPathExtractor
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.graph_stores.falkordb import FalkorDBGraphStore

sys.path.insert(0, "src")
from scrape import build_documents, load_config


def run(book: int, config: dict):
    llm = Ollama(model=config["ollama_model"], request_timeout=300)
    embed_model = OllamaEmbedding(model_name=config["ollama_model"])

    graph_store = FalkorDBGraphStore(
        url=f"redis://{config['falkordb_host']}:{config['falkordb_port']}",
        database="odyssey_open",
    )

    # FalkorDB versions prior to 0.4.2 omit this attribute; set it explicitly
    if not hasattr(graph_store, "supports_vector_queries"):
        graph_store.supports_vector_queries = False

    kg_extractor = DynamicLLMPathExtractor(
        llm=llm,
        max_triplets_per_chunk=config["max_triplets_open"],
        num_workers=4,
    )

    docs = build_documents(book, config)

    print(f"Running open-domain extraction on {len(docs)} chunks...")
    index = PropertyGraphIndex.from_documents(
        docs,
        kg_extractors=[kg_extractor],
        property_graph_store=graph_store,
        embed_model=embed_model,
        show_progress=True,
    )
    print("Done. Graph stored in FalkorDB as 'odyssey_open'.")
    return index


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", type=int, default=1)
    args = parser.parse_args()

    config = load_config()
    run(args.book, config)
