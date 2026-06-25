# SQLScholar – SQL Learning and Performance Analytics System

A Python CLI application that helps students practise SQL through interactive
terminal sessions with performance tracking and personalised recommendations.

---

## Project Structure

```
SQLScholar/
├── sqlscholar.py        ← Main application (run this)
├── generate_dataset.py  ← Run once to create questions.csv
├── questions.csv        ← Auto-generated: 1,500 SQL Q&A pairs
└── progress.csv         ← Auto-created: your attempt log
```

---

## Requirements

- **Python 3.7 or later** (no external libraries required)

Check your Python version:

```bash
python --version
```

or on some systems:

```bash
python3 --version
```

---

## How to Run (Step-by-Step)

### Step 1 – Open the project in VS Code

1. Open **Visual Studio Code**
2. Go to `File → Open Folder` and select the `SQLScholar` folder
3. Open the **Terminal** with `` Ctrl + ` `` (backtick)

---

### Step 2 – Generate the dataset (run once only)

In the VS Code terminal, run:

```powershell
python generate_dataset.py
```

Expected output:

```
Generating dataset …
Saved 1500 questions to 'questions.csv'.
  AGGREGATE FUNCTIONS       250
  GROUP BY                  250
  JOIN                      250
  ORDER BY                  250
  SELECT                    250
  WHERE                     250
```

This creates `questions.csv`. You only need to do this **once**.

---

### Step 3 – Start SQLScholar

```powershell
python sqlscholar.py
```

You will see:

```
╔══════════════════════════════════════════════════╗
║          SQLScholar  –  SQL Learning CLI          ║
╚══════════════════════════════════════════════════╝

  Loading dataset …
  Loaded 1500 questions from 'questions.csv'.

  ┌────────────────────────────────┐
  │  1  Start practice session     │
  │  2  View performance analytics │
  │  3  Get study recommendations  │
  │  4  Show all recommendations   │
  │  5  Reset progress             │
  │  6  Exit                       │
  └────────────────────────────────┘

  Choose an option [1-6]:
```

---

## Menu Options Explained

| Option | Description                                                                                                                                                         |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**  | Start a practice quiz. Enter how many questions you want (default: 10), and optionally filter by topic (SELECT, WHERE, etc.). Type your SQL answer and press Enter. |
| **2**  | View your performance dashboard: overall accuracy, topic-wise accuracy bar chart, and your strongest/weakest topics.                                                |
| **3**  | View your analytics **plus** personalised recommendations for topics where you are below the threshold.                                                             |
| **4**  | Show the full study guide for all six SQL topics.                                                                                                                   |
| **5**  | Reset your progress (deletes `progress.csv`).                                                                                                                       |
| **6**  | Exit the application.                                                                                                                                               |

---

## During a Practice Session

- Type your SQL query and press **Enter** to submit.
- Type `skip` to skip a question without it being logged.
- Type `quit` or `exit` to end the session early.
- SQL answers are **case-insensitive** and **whitespace-insensitive** (the system normalises both your answer and the correct answer before comparing).

**Example:**

```
  Question 1/10  [SELECT  |  Easy]
  Write a SQL query to retrieve all records from the students table.

  Your SQL > select * from students
  ✓ Correct!
```

---

## Filtering by Topic

When starting a session (Option 1), you can filter questions to a specific topic:

```
Filter by topic? (SELECT / WHERE / ORDER BY / GROUP BY / JOIN / AGGREGATE FUNCTIONS / Enter for all):
```

Type one of the topic names **exactly** (case-insensitive) or press **Enter** to practise all topics.

---

## Understanding the Analytics Dashboard

```
  ─── Performance Dashboard ───────────────────────────
  Overall Accuracy  : 68.0%  (34/50 correct)

  Topic-wise Accuracy:
    AGGREGATE FUNCTIONS    ████████████████░░░░ 80.0%
    GROUP BY               ███████░░░░░░░░░░░░░ 38.0%
    JOIN                   █████░░░░░░░░░░░░░░░ 29.0%
    ORDER BY               ███████████████░░░░░ 75.0%
    SELECT                 █████████░░░░░░░░░░░ 45.0%
    WHERE                  ██████████████░░░░░░ 70.0%

  Strongest Topic : AGGREGATE FUNCTIONS
  Weakest Topic   : JOIN
```

- **Green bar** = 70 % or above (good)
- **Yellow bar** = 50–69 % (needs practice)
- **Red bar** = below 50 % (focus here)

---

## Common Issues

| Problem                                  | Solution                                                                    |
| ---------------------------------------- | --------------------------------------------------------------------------- |
| `python: command not found`              | Try `python3 sqlscholar.py` instead                                         |
| `Dataset file 'questions.csv' not found` | Run `python generate_dataset.py` first                                      |
| Colours not showing on Windows           | Colours are automatically disabled on Windows; the app still works normally |

---

## Dataset Source

Questions are derived from the **WikiSQL** benchmark dataset:
https://huggingface.co/datasets/Salesforce/wikisql

WikiSQL contains 80,654 annotated natural-language–SQL pairs across 24,241 HTML tables,
making it an ideal source of varied, well-structured SQL practice questions.
