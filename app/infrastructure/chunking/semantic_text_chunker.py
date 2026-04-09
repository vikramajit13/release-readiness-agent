import re
from app.ports.services.chunker_port import ChunkerPort, ChunkResult
from __future__ import annotations




class SemanticTextChunker(ChunkerPort):
    """
    Paragraph-first chunker with:
    - heading/list awareness
    - sentence fallback for long sections
    - overlap by sentence tail
    - character offsets for citations
    - lightweight token estimation
    """

    def __init__(
        self,
        target_chars: int = 800,
        overlap_sents: int = 1,
        min_chars: int = 200,
        max_chars_per_paragraph: int | None = None,
    ) -> None:
        self.target_chars = target_chars
        self.overlap_sents = overlap_sents
        self.min_chars = min_chars
        self.max_chars_per_paragraph = max_chars_per_paragraph or int(target_chars * 1.5)

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def normalize_for_search(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    @staticmethod
    def estimate_tokens(text: str) -> int:
        # crude but useful approximation
        return max(1, len(text) // 4)

    @staticmethod
    def is_heading(line: str) -> bool:
        line = line.strip()
        if not line:
            return False
        if len(line) > 120:
            return False
        if re.match(r"^(#{1,6}\s+)", line):
            return True
        if re.match(r"^\d+(\.\d+)*\s+[A-Z]", line):
            return True
        if line.isupper() and len(line.split()) <= 10:
            return True
        return False

    @staticmethod
    def is_list_item(line: str) -> bool:
        line = line.strip()
        return bool(
            re.match(r"^([-*•]\s+)", line)
            or re.match(r"^\d+[\.\)]\s+", line)
            or re.match(r"^[a-zA-Z][\.\)]\s+", line)
        )

    def split_blocks(self, text: str) -> list[dict]:
        """
        Split into paragraph-like blocks while preserving approximate offsets.
        Also keeps headings/list items as separate blocks where possible.
        """
        text = self.normalize_whitespace(text)
        blocks: list[dict] = []

        pos = 0
        for para in re.split(r"\n\n+", text):
            para = para.strip()
            if not para:
                continue

            start = text.find(para, pos)
            if start == -1:
                start = pos
            end = start + len(para)
            pos = end

            lines = [ln.strip() for ln in para.split("\n") if ln.strip()]

            # preserve headings/list-heavy sections more carefully
            if len(lines) > 1 and any(self.is_heading(ln) or self.is_list_item(ln) for ln in lines):
                running_start = start
                for ln in lines:
                    ln_start = text.find(ln, running_start)
                    if ln_start == -1:
                        ln_start = running_start
                    ln_end = ln_start + len(ln)
                    running_start = ln_end
                    blocks.append(
                        {
                            "text": ln,
                            "char_start": ln_start,
                            "char_end": ln_end,
                            "kind": "heading" if self.is_heading(ln) else "list_item" if self.is_list_item(ln) else "line",
                        }
                    )
            else:
                kind = "heading" if len(lines) == 1 and self.is_heading(lines[0]) else "paragraph"
                blocks.append(
                    {
                        "text": para,
                        "char_start": start,
                        "char_end": end,
                        "kind": kind,
                    }
                )

        return blocks

    def split_sentences_with_offsets(self, text: str, base_offset: int = 0) -> list[dict]:
        """
        Better than the original regex:
        - keeps sentence punctuation attached
        - tolerates newlines
        - avoids tiny junk spans
        """
        sentence_pattern = re.compile(
            r"""
            .*?
            (?:
                [.!?]+(?=\s+|$)     # normal sentence end
                |
                (?=\n[-*•]\s)       # before bullet list starts
                |
                (?=\n\d+[\.\)]\s)   # before numbered list starts
                |
                $                   # end of text
            )
            """,
            re.VERBOSE | re.DOTALL,
        )

        results: list[dict] = []
        cursor = 0
        for match in sentence_pattern.finditer(text):
            sent = match.group(0).strip()
            if not sent:
                continue
            if len(sent) < 20:
                continue

            sent_start = text.find(sent, cursor)
            if sent_start == -1:
                sent_start = cursor
            sent_end = sent_start + len(sent)
            cursor = sent_end

            lowered = sent.lower()
            if "http" in lowered or "@" in lowered:
                continue

            results.append(
                {
                    "text": sent,
                    "char_start": base_offset + sent_start,
                    "char_end": base_offset + sent_end,
                }
            )

        return results

    def explode_large_block(self, block: dict) -> list[dict]:
        text = block["text"]
        if len(text) <= self.max_chars_per_paragraph:
            return [block]

        if block["kind"] in {"heading", "list_item"}:
            return [block]

        sentences = self.split_sentences_with_offsets(
            text=text,
            base_offset=block["char_start"],
        )
        return sentences if sentences else [block]

    def chunk(self, text: str, metadata: dict | None = None) -> list[ChunkResult]:
        metadata = metadata or {}
        text = self.normalize_whitespace(text)

        raw_blocks = self.split_blocks(text)

        blocks: list[dict] = []
        for block in raw_blocks:
            blocks.extend(self.explode_large_block(block))

        chunks: list[ChunkResult] = []
        buffer: list[dict] = []

        def buffered_text(parts: list[dict]) -> str:
            return "\n\n".join(p["text"] for p in parts).strip()

        def flush() -> None:
            nonlocal buffer
            if not buffer:
                return

            chunk_text = buffered_text(buffer)
            if len(chunk_text) < self.min_chars:
                return

            chunk_start = buffer[0]["char_start"]
            chunk_end = buffer[-1]["char_end"]

            chunk_index = len(chunks)
            chunks.append(
                ChunkResult(
                    chunk_index=chunk_index,
                    text=chunk_text,
                    metadata={
                        **metadata,
                        "char_start": chunk_start,
                        "char_end": chunk_end,
                        "char_length": len(chunk_text),
                        "estimated_tokens": self.estimate_tokens(chunk_text),
                        "normalized_text": self.normalize_for_search(chunk_text),
                    },
                )
            )

        for block in blocks:
            block_text = block["text"]
            current_text = buffered_text(buffer) if buffer else ""

            proposed_len = len(current_text) + (2 if current_text else 0) + len(block_text)
            if proposed_len <= self.target_chars:
                buffer.append(block)
                continue

            flush()

            if self.overlap_sents > 0 and chunks:
                prev_tail = self.split_sentences_with_offsets(chunks[-1].text)
                tail_parts = prev_tail[-self.overlap_sents :] if prev_tail else []
                overlap_text = " ".join(p["text"] for p in tail_parts).strip()

                if overlap_text:
                    overlap_len = len(overlap_text)
                    overlap_start = max(chunks[-1].metadata["char_end"] - overlap_len, chunks[-1].metadata["char_start"])
                    buffer = [
                        {
                            "text": overlap_text,
                            "char_start": overlap_start,
                            "char_end": chunks[-1].metadata["char_end"],
                            "kind": "overlap",
                        },
                        block,
                    ]
                else:
                    buffer = [block]
            else:
                buffer = [block]

        flush()
        return chunks