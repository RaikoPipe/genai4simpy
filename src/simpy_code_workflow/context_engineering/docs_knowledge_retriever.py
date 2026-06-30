from pathlib import Path
from typing import Optional

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


class SimPyKnowledgeRetriever:
    ALWAYS_LOADED = ["api_reference"]

    def __init__(
        self,
        docs_path: Optional[Path] = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        relevance_threshold: float = 0.3,
    ):
        self.docs_path = docs_path or Path(__file__).parent / "resources" / "simpy_docs"
        self.relevance_threshold = relevance_threshold
        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")]
        )
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.cached_docs = self._load_core_docs()
        self.vectorstore = self._build_vectorstore()

    def _load_core_docs(self) -> str:
        cached = []
        for folder_name in self.ALWAYS_LOADED:
            folder_path = self.docs_path / folder_name
            for md_file in sorted(folder_path.glob("**/*.md")):
                cached.append(md_file.read_text())
        return "\n\n---\n\n".join(cached)

    def _build_vectorstore(self) -> Chroma:
        chunks = []

        for folder in self.docs_path.iterdir():
            if not folder.is_dir() or folder.name in self.ALWAYS_LOADED:
                continue

            for md_file in folder.glob("**/*.md"):
                text = md_file.read_text()
                split_docs = self.splitter.split_text(text)

                for doc in split_docs:
                    # Build a header breadcrumb for context
                    headers = [
                        doc.metadata[h]
                        for h in ("h1", "h2", "h3")
                        if h in doc.metadata
                    ]
                    breadcrumb = " > ".join(headers) if headers else ""

                    doc.metadata.update({
                        "source": md_file.name,
                        "folder": folder.name,
                        "doc_type": self._classify_doc(folder.name, md_file.name),
                        "breadcrumb": breadcrumb,
                    })
                chunks.extend(split_docs)

        return Chroma.from_documents(chunks, self.embeddings)

    def _classify_doc(self, folder_name: str, filename: str) -> str:
        combined = f"{folder_name}/{filename}".lower()
        if "api" in combined or "reference" in combined:
            return "api"
        elif "guide" in combined or "topical" in combined:
            return "guide"
        elif "example" in combined:
            return "example"
        return "tutorial"

    def retrieve(self, query: str, k: int = 4) -> str:
        """Returns cached docs + relevance-filtered retrieved chunks."""
        results = self.vectorstore.similarity_search_with_relevance_scores(query, k=k)

        # Filter by threshold and deduplicate
        seen_content = set()
        retrieved_docs: list[Document] = []
        for doc, score in results:
            if score < self.relevance_threshold:
                continue
            content_hash = hash(doc.page_content)
            if content_hash in seen_content:
                continue
            seen_content.add(content_hash)
            retrieved_docs.append(doc)

        # Format with breadcrumbs for LLM context
        retrieved_sections = []
        for doc in retrieved_docs:
            breadcrumb = doc.metadata.get("breadcrumb", "")
            header = f"[{breadcrumb}]" if breadcrumb else ""
            source = doc.metadata.get("source", "")
            retrieved_sections.append(
                f"<!-- source: {source} {header} -->\n{doc.page_content}"
            )

        retrieved_text = "\n\n---\n\n".join(retrieved_sections)

        if retrieved_text:
            return f"{self.cached_docs}\n\n---\n\n## Retrieved Context\n\n{retrieved_text}"
        return self.cached_docs


if __name__ == "__main__":
    retriever = SimPyKnowledgeRetriever()
    result = retriever.retrieve("How to create a Part instance?", k=3)
    print(result)