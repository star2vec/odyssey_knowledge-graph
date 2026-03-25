"""Stage 1: Scrape and chunk Odyssey text from theoi.com."""
import argparse
import yaml
import requests
from bs4 import BeautifulSoup
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter


def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)


def scrape_book(book: int, base_url: str) -> str:
    url = base_url.format(book=book)
    print(f"Fetching: {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # theoi.com main content is in <p> tags inside the main content div
    # Remove nav, header, footer, script, style elements
    for tag in soup(["script", "style", "nav", "header", "footer", "a"]):
        tag.decompose()

    # Grab all paragraph text
    paragraphs = soup.find_all("p")
    text = "\n\n".join(p.get_text(separator=" ", strip=True) for p in paragraphs if p.get_text(strip=True))
    return text


def build_documents(book: int, config: dict) -> list[Document]:
    text = scrape_book(book, config["text_base_url"])

    splitter = SentenceSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
    )
    chunks = splitter.split_text(text)

    docs = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            text=chunk,
            metadata={"book": book, "chunk_index": i},
        )
        docs.append(doc)

    print(f"Book {book}: {len(docs)} chunks")
    return docs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", type=int, default=1)
    args = parser.parse_args()

    config = load_config()
    docs = build_documents(args.book, config)

    # Quick preview
    for i, doc in enumerate(docs):
        print(f"\n--- Chunk {i} ---")
        print(doc.text[:200])
