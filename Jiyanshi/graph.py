import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

from neo4j import GraphDatabase
from dotenv import load_dotenv

# =========================
#  CONFIG + CONNECTION
# =========================

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
SUBJECT_NAME = os.getenv("SUBJECT_NAME", "Unified Textbook Knowledge Graph")

if not (NEO4J_URI and NEO4J_USER and NEO4J_PASSWORD):
    raise RuntimeError("Neo4j URI / USER / PASSWORD missing in .env")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# =========================
#  DATA STRUCTURES
# =========================

@dataclass
class Topic:
    id: str
    title: str
    level: int  # 1 = topic, 2 = subtopic
    parent_id: Optional[str] = None


@dataclass
class Unit:
    title: str
    number: Optional[str]
    block_name: str
    text: str
    topics: List[Topic] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)


# =========================
#  TEXTBOOK PARSING
# =========================

BLOCK_KEYWORDS = {
    "Photography": [
        "shutter", "aperture", "iso", "lens", "photo editing",
        "types of photography", "depth of field", "exposure triangle"
    ],
    "ICT For Development": [
        "ict for development", "ict4d", "digital divide",
        "poverty reduction", "rural development", "e-governance",
        "knowledge society"
    ],
    "Digital Media Literacy": [
        "digital media literacy", "media literacy", "virtual world",
        "interactive multimedia", "mojo", "mobile journalism",
        "political participation", "film genres", "advertising literacy"
    ],
    "Report Writing": [
        "report writing", "abstract", "executive summary",
        "methodology", "literature review", "acknowledgements",
        "research report"
    ],
    "Data Analysis": [
        "mean median mode", "quartile range", "variance",
        "standard deviation", "frequency distribution",
        "analysing and interpreting data"
    ],
}

DEFAULT_BLOCK = "Other"


def guess_block(text_chunk: str) -> str:
    """Heuristically assign a block name based on keywords in the unit text."""
    lower = text_chunk.lower()
    for block, keywords in BLOCK_KEYWORDS.items():
        if any(k in lower for k in keywords):
            return block
    return DEFAULT_BLOCK


UNIT_PATTERN = re.compile(
    r"^\s*UNIT\s+(\d+)\s*[:\-]?\s*(.+)$", re.IGNORECASE
)

TOPIC_LEVEL1_PATTERN = re.compile(
    r"^(\d+\.\d+)\s+(.+)$"
)

TOPIC_LEVEL2_PATTERN = re.compile(
    r"^(\d+\.\d+\.\d+)\s+(.+)$"
)


def parse_units(full_text: str) -> List[Unit]:
    """Split full text into Units based on 'UNIT X' headings."""
    lines = full_text.splitlines()
    units: List[Unit] = []

    current_title = None
    current_number = None
    current_lines: List[str] = []

    def flush_current():
        nonlocal current_title, current_number, current_lines
        if current_title is None:
            return
        text_chunk = "\n".join(current_lines)
        block = guess_block(text_chunk)
        units.append(
            Unit(
                title=current_title.strip(),
                number=current_number,
                block_name=block,
                text=text_chunk,
            )
        )
        current_title = None
        current_number = None
        current_lines = []

    for line in lines:
        m = UNIT_PATTERN.match(line)
        if m:
            # new unit starts
            flush_current()
            current_number = m.group(1)
            current_title = line.strip()  # full line with 'UNIT X ...'
            current_lines = []
        else:
            if current_title is not None:
                current_lines.append(line)

    # last one
    flush_current()

    return units


def extract_topics_concepts_questions(units: List[Unit]) -> None:
    """Fill topics, concepts and questions for each unit."""
    for unit in units:
        lines = unit.text.splitlines()

        # topic parsing
        last_topic_id = None
        for line in lines:
            l = line.strip()
            if not l:
                continue

            m2 = TOPIC_LEVEL2_PATTERN.match(l)
            if m2:
                num, title = m2.groups()
                topic_id = f"{unit.number}.{num}"
                unit.topics.append(
                    Topic(
                        id=topic_id,
                        title=title.strip(),
                        level=2,
                        parent_id=last_topic_id,
                    )
                )
                continue

            m1 = TOPIC_LEVEL1_PATTERN.match(l)
            if m1:
                num, title = m1.groups()
                topic_id = f"{unit.number}.{num}"
                unit.topics.append(
                    Topic(
                        id=topic_id,
                        title=title.strip(),
                        level=1,
                        parent_id=None,
                    )
                )
                last_topic_id = topic_id

        # concepts from KEY WORDS section
        in_keywords = False
        for line in lines:
            l = line.strip()
            if not l:
                continue

            if "KEY WORDS" in l.upper():
                in_keywords = True
                continue
            if in_keywords and ("FURTHER READINGS" in l.upper() or l.startswith("8.10 FURTHER")):
                in_keywords = False
                continue

            if in_keywords:
                # lines like "- Canvas: the main workspace ..."
                if l.startswith("-"):
                    concept = l[1:].strip()
                    # keep only term before ':' if present
                    term = concept.split(":", 1)[0].strip()
                    if term:
                        unit.concepts.append(term)

        # questions from "Check Your Progress"
        in_questions = False
        for line in lines:
            l = line.strip()
            if "CHECK YOUR PROGRESS" in l.upper():
                in_questions = True
                continue

            if in_questions:
                # stop if we hit another heading
                if UNIT_PATTERN.match(l):
                    in_questions = False
                    continue
                if re.match(r"^\d+\.\d+", l) or "KEY WORDS" in l.upper():
                    # new numbered heading
                    in_questions = False
                    continue

                # numbered question: "1. What is ..."
                qmatch = re.match(r"^\d+\.\s*(.+)$", l)
                if qmatch:
                    question_text = qmatch.group(1).strip()
                    unit.questions.append(question_text)

        # de-duplicate
        unit.concepts = list(dict.fromkeys(unit.concepts))
        unit.questions = list(dict.fromkeys(unit.questions))


# =========================
#  NEO4J WRITE HELPERS
# =========================

def merge_subject(tx, subject_name: str):
    tx.run(
        """
        MERGE (:Subject {name: $name})
        """,
        name=subject_name,
    )


def merge_block(tx, subject_name: str, block_name: str):
    tx.run(
        """
        MERGE (s:Subject {name: $subject})
        MERGE (b:Block {name: $block})
        MERGE (s)-[:HAS_BLOCK]->(b)
        """,
        subject=subject_name,
        block=block_name,
    )


def merge_unit(tx, block_name: str, unit: Unit):
    tx.run(
        """
        MATCH (b:Block {name: $block})
        MERGE (u:Unit {title: $title})
          ON CREATE SET u.number = $number
        MERGE (b)-[:HAS_UNIT]->(u)
        """,
        block=block_name,
        title=unit.title,
        number=unit.number,
    )


def merge_topic(tx, unit_title: str, topic: Topic):
    if topic.level == 1:
        tx.run(
            """
            MATCH (u:Unit {title: $unit_title})
            MERGE (t:Topic {id: $id})
              ON CREATE SET t.title = $title
            MERGE (u)-[:HAS_TOPIC]->(t)
            """,
            unit_title=unit_title,
            id=topic.id,
            title=topic.title,
        )
    else:
        # level 2: subtopic
        tx.run(
            """
            MATCH (u:Unit {title: $unit_title})
            MERGE (st:Subtopic {id: $id})
              ON CREATE SET st.title = $title
            MERGE (u)-[:HAS_SUBTOPIC]->(st)
            """,
            unit_title=unit_title,
            id=topic.id,
            title=topic.title,
        )


def merge_concept(tx, unit_title: str, concept: str):
    tx.run(
        """
        MATCH (u:Unit {title: $unit_title})
        MERGE (c:Concept {name: $name})
        MERGE (u)-[:HAS_CONCEPT]->(c)
        """,
        unit_title=unit_title,
        name=concept,
    )


def merge_question(tx, unit_title: str, question: str):
    tx.run(
        """
        MATCH (u:Unit {title: $unit_title})
        MERGE (q:Question {text: $text})
        MERGE (u)-[:HAS_QUESTION]->(q)
        """,
        unit_title=unit_title,
        text=question,
    )


# =========================
#  MAIN BUILD FUNCTION
# =========================

def build_knowledge_graph(text_path: str):
    with open(text_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    print("📘 Parsing units from textbook...")
    units = parse_units(full_text)
    print(f"   → Found {len(units)} units")

    print("🔎 Extracting topics, concepts, questions...")
    extract_topics_concepts_questions(units)

    # Show quick summary
    for u in units:
        print(f"\n[UNIT] {u.title} | Block = {u.block_name}")
        print(f"   Topics: {len(u.topics)}, Concepts: {len(u.concepts)}, Questions: {len(u.questions)}")

    with driver.session() as session:
        print("\n🧱 Creating Subject node...")
        session.execute_write(merge_subject, SUBJECT_NAME)

        # create all blocks that appear
        blocks = sorted({u.block_name for u in units})
        print(f"🧱 Creating Blocks: {blocks}")
        for b in blocks:
            session.execute_write(merge_block, SUBJECT_NAME, b)

        print("🧱 Creating Units, Topics, Concepts, Questions...")
        for u in units:
            session.execute_write(merge_unit, u.block_name, u)
            for t in u.topics:
                session.execute_write(merge_topic, u.title, t)
            for c in u.concepts:
                session.execute_write(merge_concept, u.title, c)
            for q in u.questions:
                session.execute_write(merge_question, u.title, q)

    print("\n✅ Knowledge Graph build complete!")
    print("Open Neo4j Browser and run, for example:")
    print("  MATCH (s:Subject)-[*1..3]->(n) RETURN s,n LIMIT 100;")
    print("  MATCH (u:Unit)-[:HAS_CONCEPT]->(c) RETURN u,c LIMIT 50;")


# =========================
#  ENTRY POINT
# =========================

if __name__ == "__main__":
    TEXT_PATH = "processed/combined_book.txt"  # keep this file in same folder
    build_knowledge_graph(TEXT_PATH)
    driver.close()
