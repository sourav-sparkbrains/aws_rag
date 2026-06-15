import numpy as np
from uuid import uuid4
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.logs import get_logger
from app.core.exceptions import ContentNotFoundException
from app.services.ingestion.base import IngestionProvider

logger = get_logger()

class PDFIngestionProvider(IngestionProvider):

    def load(self, path: str) -> list[Document]:
        loader = PyMuPDFLoader(path)
        return loader.load()

    @staticmethod
    def _analyze_chunk_sizes(word_counts: list[int]) -> dict[str,int]:

        arr = np.array(word_counts)

        mean = arr.mean()
        std = arr.std()

        p50 = np.percentile(arr, 50)
        p75 = np.percentile(arr, 75)

        variance_ratio = std / mean if mean else 0

        # choose base document size
        base_words = p50 if variance_ratio > 0.7 else p75

        # convert words to tokens (1 word is 0.7 token so 1 token is 1.33 word)
        tokens = base_words * 1.33

        # parent chunk (larger context)
        parent_chunk = int(tokens * 0.35)
        parent_overlap = int(parent_chunk * 0.15)

        parent_chunk = max(parent_chunk, 800)

        # child chunk (retrieval unit)
        child_chunk = int(parent_chunk * 0.40)
        child_overlap = int(child_chunk * 0.20)

        child_chunk = max(child_chunk, 250)

        token_to_char = 4

        parent_chunk = parent_chunk * token_to_char
        parent_overlap = parent_overlap * token_to_char
        child_chunk = child_chunk * token_to_char
        child_overlap = child_overlap * token_to_char

        return {
            "parent_chunk": parent_chunk,
            "parent_overlap": parent_overlap,
            "child_chunk": child_chunk,
            "child_overlap": child_overlap
        }

    @staticmethod
    def _split_into_chunks(
            documents: list[Document],
            parent_splitter: RecursiveCharacterTextSplitter,
            child_splitter: RecursiveCharacterTextSplitter,
    ) -> tuple[list, list] | None:

        parent_docs = []
        child_docs = []

        for doc in documents:
            if doc.page_content:
                parent_chunks = parent_splitter.split_text(doc.page_content)
                for chunk in parent_chunks:
                    parent_id = str(uuid4())
                    parent_docs.append(Document(
                        page_content=chunk,
                        metadata={"parent_id": parent_id, "page_no": doc.metadata.get("page")}
                    ))
                    child_chunks = child_splitter.split_text(chunk)
                    for child in child_chunks:
                        child_docs.append(Document(
                            page_content=child,
                            metadata={"child_id": str(uuid4()), "parent_id": parent_id,
                                      "page_no": doc.metadata.get("page")}
                        ))

        logger.info(f"Created {len(parent_docs)} parent chunks")
        logger.info(f"Created {len(child_docs)} child chunks")

        return parent_docs, child_docs

    def chunk(self, documents: list[Document]) -> tuple[list[Document], list[Document]]:

        word_counts = [
            len(doc.page_content.split())
            for doc in documents
            if doc.page_content
        ]

        if not word_counts:
            logger.error("PDF is empty")
            raise ContentNotFoundException(
                message="PDF is empty",
                context={"details": "PDF is empty, kindly provide a pdf that has content"},
            )

        chunk_config = self._analyze_chunk_sizes(word_counts)

        logger.info(
            f"parent_chunk={chunk_config['parent_chunk']}, "
            f"parent_overlap={chunk_config['parent_overlap']}, "
            f"child_chunk={chunk_config['child_chunk']}, "
            f"child_overlap={chunk_config['child_overlap']}"
        )

        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_config['parent_chunk'],
            chunk_overlap=chunk_config['parent_overlap'],
        )

        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_config['child_chunk'],
            chunk_overlap=chunk_config['child_overlap'],
        )

        parent_docs, child_docs = self._split_into_chunks(
                                documents,
                                parent_splitter,
                                child_splitter,
                                )

        return parent_docs, child_docs