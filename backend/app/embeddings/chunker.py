"""Document Chunking"""


class Chunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list:
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = " ".join(words[i : i + self.chunk_size])
            chunks.append(chunk)

        return chunks


chunker = Chunker()
