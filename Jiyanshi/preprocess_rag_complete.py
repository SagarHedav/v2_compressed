import os
import re
import json
import logging
from typing import List, Dict

# =========================
# LOGGER CONFIG
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger("RAG-PREPROCESSOR")

# =========================
# CONFIG
# =========================

INPUT_TEXT_FILE = "combined_book.txt"
OUTPUT_DIR = "processed"
BOOK_NAME = "Digital Photography"

MAX_TOKENS = 250
OVERLAP = 50

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# SECTION DETECTION
# =========================

# STRICT numeric hierarchy only
SECTION_PATTERN = re.compile(
    r"^\s*(\d+(?:\.\d+){0,3})\s+(.+)$"
)

def split_into_sections(text: str) -> List[Dict]:
    logger.info("[SECTION DETECTION START]")

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    sections = []
    current = None

    for line in lines:
        m = SECTION_PATTERN.match(line)

        if m:
            section_id = m.group(1)
            title = m.group(2)

            # 🚫 reject page numbers like "44 Digital Photography"
            if section_id.isdigit() and int(section_id) > 30:
                continue

            if current:
                current["content"] = " ".join(current["content"]).strip()
                sections.append(current)

            logger.info(f"Section found → {section_id} | {title}")

            current = {
                "book": BOOK_NAME,
                "section_id": section_id,
                "section_title": title,
                "content": []
            }
        else:
            if current:
                current["content"].append(line)

    if current:
        current["content"] = " ".join(current["content"]).strip()
        sections.append(current)

    logger.info(f"[SECTION DETECTION END] Total sections: {len(sections)}")
    return sections

# =========================
# SAFE CHUNKING (ZERO SKIP)
# =========================

def chunk_text(text: str,
               max_tokens: int = MAX_TOKENS,
               overlap: int = OVERLAP) -> List[str]:

    words = text.split()

    # 🔒 SAFETY: ALWAYS at least one chunk
    if len(words) <= max_tokens:
        return [" ".join(words)]

    chunks = []
    start = 0

    while start < len(words):
        end = start + max_tokens
        chunks.append(" ".join(words[start:end]))
        start += max_tokens - overlap

    return chunks

def build_vector_chunks(sections: List[Dict]) -> List[Dict]:
    logger.info("[CHUNKING START]")

    all_chunks = []

    for sec in sections:
        chunks = chunk_text(sec["content"])
        logger.info(f"Section {sec['section_id']} → {len(chunks)} chunks")

        for idx, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "metadata": {
                    "book": sec["book"],
                    "section_id": sec["section_id"],
                    "section_title": sec["section_title"],
                    "chunk_index": idx
                }
            })

    logger.info(f"[CHUNKING END] Total chunks: {len(all_chunks)}")
    return all_chunks

# =========================
# PIPELINE
# =========================

def run_pipeline():
    logger.info("[PIPELINE START]")

    if not os.path.exists(INPUT_TEXT_FILE):
        raise FileNotFoundError(f"{INPUT_TEXT_FILE} not found")

    with open(INPUT_TEXT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    sections = split_into_sections(text)
    vector_chunks = build_vector_chunks(sections)

    # =========================
    # SAVE OUTPUTS
    # =========================

    with open(os.path.join(OUTPUT_DIR, "vector_chunks.json"),
              "w", encoding="utf-8") as f:
        json.dump(vector_chunks, f, indent=2, ensure_ascii=False)

    with open(os.path.join(OUTPUT_DIR, "sections.json"),
              "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)

    logger.info("[PIPELINE COMPLETE]")
    logger.info(f"Sections: {len(sections)}")
    logger.info(f"Chunks: {len(vector_chunks)}")

# =========================

if __name__ == "__main__":
    run_pipeline()
