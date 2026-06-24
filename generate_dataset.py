
import csv
import random

random.seed(42)  

OUTPUT_FILE = "questions.csv"

# Template banks 


TABLES = [
    ("students",    ["student_id", "name", "age", "grade", "course"]),
    ("employees",   ["emp_id", "emp_name", "department", "salary", "hire_date"]),
    ("products",    ["product_id", "product_name", "category", "price", "stock"]),
    ("orders",      ["order_id", "customer_id", "order_date", "total_amount", "status"]),
    ("customers",   ["customer_id", "first_name", "last_name", "city", "email"]),
    ("courses",     ["course_id", "course_name", "credits", "instructor", "department"]),
    ("departments", ["dept_id", "dept_name", "manager", "budget", "location"]),
    ("sales",       ["sale_id", "product_id", "quantity", "sale_date", "revenue"]),
    ("books",       ["book_id", "title", "author", "genre", "publish_year"]),
    ("flights",     ["flight_id", "origin", "destination", "airline", "price"]),
]

def rand_table():
    return random.choice(TABLES)

def rand_col(cols):
    return random.choice(cols)

def rand_two_cols(cols):
    c = random.sample(cols, min(2, len(cols)))
    return c[0], c[1]

# Question generators per topic

def make_select(n):
    rows = []
    difficulties = ["Easy"] * (n // 2) + ["Medium"] * (n // 3) + ["Hard"] * (n - n // 2 - n // 3)
    random.shuffle(difficulties)
    for i, diff in enumerate(difficulties):
        tbl, cols = rand_table()
        if diff == "Easy":
            q = f"Write a SQL query to retrieve all records from the {tbl} table."
            a = f"SELECT * FROM {tbl}"
        elif diff == "Medium":
            c1, c2 = rand_two_cols(cols)
            q = f"Write a SQL query to select the {c1} and {c2} columns from the {tbl} table."
            a = f"SELECT {c1},{c2} FROM {tbl}"
        else:
            c1, c2 = rand_two_cols(cols)
            q = f"Write a SQL query to select distinct values of {c1} and {c2} from {tbl}."
            a = f"SELECT DISTINCT {c1},{c2} FROM {tbl}"
        rows.append(("SELECT", diff, q, a))
    return rows

def make_where(n):
    rows = []
    ops = ["=", ">", "<", ">=", "<=", "!="]
    for _ in range(n):
        tbl, cols = rand_table()
        col = rand_col(cols)
        op  = random.choice(ops)
        val = random.randint(1, 100)
        diff = "Easy" if op == "=" else ("Medium" if op in (">","<") else "Hard")
        q = (f"Write a SQL query to select all records from {tbl} "
             f"where {col} {op} {val}.")
        a = f"SELECT * FROM {tbl} WHERE {col}{op}{val}"
        rows.append(("WHERE", diff, q, a))
    return rows

def make_orderby(n):
    rows = []
    for _ in range(n):
        tbl, cols = rand_table()
        col  = rand_col(cols)
        dire = random.choice(["ASC", "DESC"])
        diff = "Easy" if dire == "ASC" else "Medium"
        q = (f"Write a SQL query to retrieve all records from {tbl} "
             f"sorted by {col} in {'ascending' if dire=='ASC' else 'descending'} order.")
        a = f"SELECT * FROM {tbl} ORDER BY {col} {dire}"
        rows.append(("ORDER BY", diff, q, a))
    return rows

def make_groupby(n):
    rows = []
    agg_fns = ["COUNT(*)", "SUM", "AVG", "MAX", "MIN"]
    for _ in range(n):
        tbl, cols = rand_table()
        grp_col  = rand_col(cols)
        agg_col  = rand_col(cols)
        fn_name  = random.choice(agg_fns)
        if fn_name == "COUNT(*)":
            agg_expr = "COUNT(*)"
            diff = "Easy"
        else:
            agg_expr = f"{fn_name}({agg_col})"
            diff = "Medium"
        q = (f"Write a SQL query to find the {fn_name.split('(')[0].lower()} "
             f"for each {grp_col} in the {tbl} table.")
        a = f"SELECT {grp_col},{agg_expr} FROM {tbl} GROUP BY {grp_col}"
        rows.append(("GROUP BY", diff, q, a))
    return rows

def make_join(n):
    join_types = [("INNER JOIN", "Medium"), ("LEFT JOIN", "Hard"), ("RIGHT JOIN", "Hard")]
    pairs = [
        ("orders",    "customers",   "customer_id"),
        ("sales",     "products",    "product_id"),
        ("students",  "courses",     "course_id"),
        ("employees", "departments", "dept_id"),
    ]
    rows = []
    for _ in range(n):
        jtype, diff = random.choice(join_types)
        t1, t2, key = random.choice(pairs)
        q = (f"Write a SQL query to perform a {jtype} between {t1} and {t2} "
             f"on the {key} column.")
        a = f"SELECT * FROM {t1} {jtype} {t2} ON {t1}.{key}={t2}.{key}"
        rows.append(("JOIN", diff, q, a))
    return rows

def make_aggregate(n):
    fns = [
        ("COUNT(*)",  "Easy",   "count the number of records in"),
        ("SUM",       "Medium", "calculate the total sum of {col} in"),
        ("AVG",       "Medium", "calculate the average of {col} in"),
        ("MAX",       "Easy",   "find the maximum value of {col} in"),
        ("MIN",       "Easy",   "find the minimum value of {col} in"),
    ]
    rows = []
    for _ in range(n):
        tbl, cols = rand_table()
        col = rand_col(cols)
        fn, diff, desc_tmpl = random.choice(fns)
        desc = desc_tmpl.format(col=col)
        if fn == "COUNT(*)":
            expr = "COUNT(*)"
        else:
            expr = f"{fn}({col})"
        q = f"Write a SQL query to {desc} the {tbl} table."
        a = f"SELECT {expr} FROM {tbl}"
        rows.append(("AGGREGATE FUNCTIONS", diff, q, a))
    return rows

# Assemble

def generate(total=1500):
    share = total // 6         
    remainder = total - share * 6

    raw = (
        make_select(share)
        + make_where(share)
        + make_orderby(share)
        + make_groupby(share)
        + make_join(share)
        + make_aggregate(share + remainder)
    )

    random.shuffle(raw)

    rows = []
    for i, (topic, difficulty, question, answer) in enumerate(raw, 1):
        rows.append({
            "id":         str(i),
            "question":   question,
            "answer":     answer,
            "topic":      topic,
            "difficulty": difficulty,
        })
    return rows

def main():
    print("Generating dataset …")
    rows = generate(1500)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id","question","answer","topic","difficulty"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} questions to '{OUTPUT_FILE}'.")


    topics = {}
    for r in rows:
        topics[r["topic"]] = topics.get(r["topic"], 0) + 1
    for t, cnt in sorted(topics.items()):
        print(f"  {t:<25} {cnt}")

if __name__ == "__main__":
    main()