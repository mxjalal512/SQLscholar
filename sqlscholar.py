import csv
import os
import sys
import random
import re
from datetime import datetime

DATASET_FILE   = "questions.csv"      
PROGRESS_FILE  = "progress.csv"      

# setting up the pass marks for each topic so the app knows when to suggest studying
THRESHOLDS = {
    "SELECT":               60,
    "WHERE":                60,
    "ORDER BY":             50,
    "GROUP BY":             50,
    "JOIN":                 50,
    "AGGREGATE FUNCTIONS":  50,
}

def _c(code, text):
    if sys.platform == "win32":
        return text
    return f"\033[{code}m{text}\033[0m"

GREEN  = lambda t: _c("92", t)
RED    = lambda t: _c("91", t)
YELLOW = lambda t: _c("93", t)
CYAN   = lambda t: _c("96", t)
BOLD   = lambda t: _c("1",  t)
DIM    = lambda t: _c("2",  t)

def load_dataset(filepath):
    if not os.path.exists(filepath):
        print(RED(f"[ERROR] Dataset file '{filepath}' not found."))
        print(DIM("       Run  generate_dataset.py  first to create it."))
        sys.exit(1)

    questions = []
    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
        for row in reader:
            questions.append({
                "id":         row["id"].strip(),
                "question":   row["question"].strip(),
                "answer":     row["answer"].strip(),
                "topic":      row["topic"].strip().upper(),
                "difficulty": row["difficulty"].strip().capitalize(),
            })

    print(DIM(f"  Loaded {len(questions)} questions from '{filepath}'."))
    return questions

def normalise_sql(query: str) -> str:
    if not isinstance(query, str):
        return ""

    s = query.strip()
    s = s.lower()
    # cleaning up the string here so extra spaces or caps don't ruin the exact match
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*,\s*", ",", s)
    s = re.sub(r"\s*\(\s*", "(", s)
    s = re.sub(r"\s*\)\s*", ")", s)
    s = s.rstrip(";").strip()
    return s

def is_correct(student_answer: str, correct_answer: str) -> bool:
    return normalise_sql(student_answer) == normalise_sql(correct_answer)

def log_attempt(question_id, topic, difficulty, result):
    file_exists = os.path.exists(PROGRESS_FILE)
    with open(PROGRESS_FILE, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if not file_exists:
            writer.writerow(["question_id", "topic", "difficulty",
                             "result", "timestamp"])
        writer.writerow([
            question_id,
            topic,
            difficulty,
            1 if result else 0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ])

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return []

    records = []
    with open(PROGRESS_FILE, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            records.append({
                "question_id": row["question_id"],
                "topic":       row["topic"].strip().upper(),
                "difficulty":  row["difficulty"].strip(),
                "result":      int(row["result"]),
                "timestamp":   row["timestamp"],
            })
    return records

def compute_analytics(records):
    if not records:
        return None

    total   = len(records)
    correct = sum(r["result"] for r in records)
    overall = round((correct / total) * 100, 1)

    # calculating the math for the dashboard to find the best and worst topics
    topic_totals  = {}
    topic_correct = {}
    for r in records:
        t = r["topic"]
        topic_totals[t]  = topic_totals.get(t, 0)  + 1
        topic_correct[t] = topic_correct.get(t, 0) + r["result"]

    topic_accuracy = {
        t: round((topic_correct[t] / topic_totals[t]) * 100, 1)
        for t in topic_totals
    }

    strongest = max(topic_accuracy, key=topic_accuracy.get)
    weakest   = min(topic_accuracy, key=topic_accuracy.get)

    return {
        "overall_accuracy": overall,
        "topic_accuracy":   topic_accuracy,
        "strongest_topic":  strongest,
        "weakest_topic":    weakest,
        "total_attempts":   total,
        "total_correct":    correct,
    }

ADVICE = {
    "SELECT": [
        "Review basic SELECT syntax: SELECT col1, col2 FROM table.",
        "Practice using SELECT with aliases (AS) for clearer output.",
        "Try selecting distinct values with SELECT DISTINCT.",
    ],
    "WHERE": [
        "Practise filtering rows with WHERE and comparison operators (=, >, <, !=).",
        "Study compound conditions using AND, OR, and NOT.",
        "Review BETWEEN, IN, and LIKE for flexible filtering.",
    ],
    "ORDER BY": [
        "Practise sorting results with ORDER BY column ASC/DESC.",
        "Try ordering by multiple columns and understand sort priority.",
        "Combine ORDER BY with LIMIT to retrieve top-N results.",
    ],
    "GROUP BY": [
        "Practise grouping rows with GROUP BY and using aggregate functions.",
        "Review the HAVING clause for filtering after aggregation.",
        "Work through examples combining GROUP BY with COUNT and SUM.",
    ],
    "JOIN": [
        "Review INNER JOIN to combine rows with matching keys.",
        "Study LEFT JOIN and RIGHT JOIN for including unmatched rows.",
        "Practise writing multi-table joins with meaningful aliases.",
    ],
    "AGGREGATE FUNCTIONS": [
        "Practise COUNT(), SUM(), AVG(), MIN(), and MAX().",
        "Combine aggregate functions with GROUP BY for grouped summaries.",
        "Try using aggregate functions inside HAVING clauses.",
    ],
}

def generate_recommendations(topic_accuracy):
    recommendations = []
    for topic, threshold in THRESHOLDS.items():
        acc = topic_accuracy.get(topic)
        if acc is None:
            recommendations.append(
                f"You have not practised {topic} yet.  "
                f"Try some {topic} questions to build confidence."
            )
        elif acc < threshold:
            for tip in ADVICE.get(topic, []):
                recommendations.append(f"[{topic}] {tip}")

    return recommendations

def print_banner():
    print()
    print(BOLD(CYAN("╔══════════════════════════════════════════════════╗")))
    print(BOLD(CYAN("║          SQLScholar  –  SQL Learning CLI          ║")))
    print(BOLD(CYAN("╚══════════════════════════════════════════════════╝")))
    print()

def print_analytics(analytics):
    if analytics is None:
        print(YELLOW("  No attempts recorded yet.  Answer some questions first!"))
        return

    print(BOLD("\n  ─── Performance Dashboard ───────────────────────────"))
    print(f"  Overall Accuracy  : {BOLD(str(analytics['overall_accuracy']) + '%')}"
          f"  ({analytics['total_correct']}/{analytics['total_attempts']} correct)")

    print("\n  Topic-wise Accuracy:")
    for topic, acc in sorted(analytics["topic_accuracy"].items()):
        bar_len = int(acc / 5)          
        bar = "█" * bar_len + "░" * (20 - bar_len)
        colour = GREEN if acc >= 70 else (YELLOW if acc >= 50 else RED)
        print(f"    {topic:<22} {colour(bar)} {acc}%")

    print(f"\n  Strongest Topic : {GREEN(analytics['strongest_topic'])}")
    print(f"  Weakest Topic   : {RED(analytics['weakest_topic'])}")

def print_recommendations(recommendations):
    print(BOLD("\n  ─── Personalised Recommendations ────────────────────"))
    if not recommendations:
        print(GREEN("  Great work – no weak areas detected!  Keep practising."))
        return
    for i, tip in enumerate(recommendations, 1):
        print(f"  {i}. {YELLOW(tip)}")

def run_quiz(questions, session_limit=None):
    random.shuffle(questions)
    pool = questions[:session_limit] if session_limit else questions

    print(BOLD(f"\n  Starting session with {len(pool)} question(s)."))
    print(DIM("  Type  'quit'  or  'exit'  at any prompt to end the session.\n"))
    print(DIM("  Type  'skip'  to skip a question without logging it.\n"))

    session_correct = 0
    session_total   = 0

    # looping through the questions and checking if the user wants to give up
    for idx, q in enumerate(pool, 1):
        print(f"  {BOLD(f'Question {idx}/{len(pool)}')}  "
              f"[{CYAN(q['topic'])}  |  {DIM(q['difficulty'])}]")
        print(f"  {q['question']}\n")

        try:
            student_answer = input("  Your SQL > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Session interrupted.")
            break

        if student_answer.lower() in ("quit", "exit"):
            print("  Ending session.")
            break

        if student_answer.lower() == "skip":
            print(DIM("  Skipped.\n"))
            continue

        result = is_correct(student_answer, q["answer"])
        log_attempt(q["id"], q["topic"], q["difficulty"], result)
        session_total += 1

        if result:
            session_correct += 1
            print(GREEN("  ✓ Correct!\n"))
        else:
            print(RED("  ✗ Incorrect."))
            print(f"  Correct answer: {DIM(q['answer'])}\n")

    if session_total > 0:
        pct = round((session_correct / session_total) * 100, 1)
        print(BOLD(f"\n  Session complete: {session_correct}/{session_total} correct ({pct}%)"))

MENU = """
  ┌────────────────────────────────┐
  │  1  Start practice session     │
  │  2  View performance analytics │
  │  3  Get study recommendations  │
  │  4  Show all recommendations   │
  │  5  Reset progress             │
  │  6  Exit                       │
  └────────────────────────────────┘
"""

def main():
    print_banner()
    print(DIM("  Loading dataset …"))
    questions = load_dataset(DATASET_FILE)
    print()

    # main menu loop handling all the user choices
    while True:
        print(MENU)
        try:
            choice = input("  Choose an option [1-6]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if choice == "1":
            try:
                limit_str = input(
                    "  How many questions per session? "
                    "[press Enter for 10]: "
                ).strip()
                limit = int(limit_str) if limit_str else 10
            except ValueError:
                limit = 10
            
            topic_choice = input(
                "  Filter by topic? "
                "(SELECT / WHERE / ORDER BY / GROUP BY / JOIN / AGGREGATE FUNCTIONS / Enter for all): "
            ).strip().upper()
            pool = [q for q in questions if q["topic"] == topic_choice] \
                   if topic_choice else questions
            if not pool:
                print(YELLOW(f"  No questions found for topic '{topic_choice}'."))
                continue
            run_quiz(pool, session_limit=limit)

        elif choice == "2":
            records   = load_progress()
            analytics = compute_analytics(records)
            print_analytics(analytics)

        elif choice == "3":
            records   = load_progress()
            analytics = compute_analytics(records)
            if analytics is None:
                print(YELLOW("  No data yet – complete some questions first."))
                continue
            recs = generate_recommendations(analytics["topic_accuracy"])
            print_analytics(analytics)
            print_recommendations(recs)

        elif choice == "4":
            print(BOLD("\n  ─── Complete Study Guide ─────────────────────────────"))
            for topic, tips in ADVICE.items():
                print(f"\n  {CYAN(BOLD(topic))}")
                for tip in tips:
                    print(f"    • {tip}")

        elif choice == "5":
            confirm = input(
                YELLOW("  This will delete all progress. Type 'yes' to confirm: ")
            ).strip().lower()
            if confirm == "yes" and os.path.exists(PROGRESS_FILE):
                os.remove(PROGRESS_FILE)
                print(GREEN("  Progress reset."))
            else:
                print(DIM("  Cancelled."))

        elif choice == "6":
            print(BOLD("\n  Thank you for using SQLScholar. Keep practising!\n"))
            break

        else:
            print(RED("  Invalid option – please enter a number between 1 and 6."))

if __name__ == "__main__":
    main()