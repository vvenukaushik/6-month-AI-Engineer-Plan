"""WHAT IS PANDAS?
Think of it like this:
- Excel/Google Sheets = you click buttons to work with tables
- Pandas = you write Python code to work with tables
- But Pandas is 1000x more powerful because you can automate EVERYTHING
 
WHY DO AI ENGINEERS NEED PANDAS?
1. AI models eat DATA — you need to clean and prepare it
2. Every dataset you'll ever work with comes as CSV, JSON, or database
3. When building RAG systems (Month 3), you'll process documents with Pandas
4. Interview questions ALWAYS include Pandas/data manipulation
 
INSTALL:
    pip install pandas
 
KEY CONCEPT — TWO DATA STRUCTURES:
    Series = a single column (like a list with labels)
    DataFrame = a whole table (like a spreadsheet with rows and columns)
 
Let's learn by doing! We'll use a real dataset.
"""

import pandas as pd

# ============================================================================
# PART 1: CREATING DATA — Building DataFrames from scratch
# ============================================================================
print("=" * 60)
print("PART 1: Creating DataFrames")
print("=" * 60)
 
# Think of a DataFrame as a dictionary where:
#   - keys = column names
#   - values = lists of data in each column
# All lists MUST be the same length!

movies_data = {
    "title": [
        "The Matrix", "Inception", "Interstellar", "The Dark Knight",
        "Pulp Fiction", "Fight Club", "Forrest Gump", "The Shawshank Redemption",
        "Parasite", "Everything Everywhere All at Once"
    ],
    "year": [1999, 2010, 2014, 2008, 1994, 1999, 1994, 1994, 2019, 2022],
    "genre": [
        "Sci-Fi", "Sci-Fi", "Sci-Fi", "Action",
        "Crime", "Drama", "Drama", "Drama",
        "Thriller", "Sci-Fi"
    ],
    "rating": [8.7, 8.8, 8.7, 9.0, 8.9, 8.8, 8.8, 9.3, 8.5, 7.8],
    "budget_millions": [63, 160, 165, 185, 8, 63, 55, 25, 11, 25],
    "revenue_millions": [463, 836, 701, 1005, 214, 101, 678, 58, 263, 141],
}

# Create the DataFrame — this is THE fundamental operation
df = pd.DataFrame(movies_data)
print(df)

# # Notice: Pandas automatically adds an INDEX (0, 1, 2...) on the left
# # The index is like row numbers in Excel

# print(df.head(3))
# print(df.tail(2))

# print(df.shape)

# print(df.columns.tolist())

# print(df.dtypes)

# print(df.describe())

# df.info()

# # ============================================================================
# # PART 2: SELECTING DATA — Getting specific rows and columns
# # ============================================================================

# print("\n--- Just the titles (Series) ---")# Method 1: Single column → returns a Series (single column)
# titles = df["title"]
# print(titles)

# # Method 2: Multiple columns → returns a DataFrame (mini table)
# print("\n--- Title and rating only (DataFrame) ---")
# subset = df[["title", "rating"]]
# print(subset)


# # ----- Selecting ROWS with loc and iloc -----
# # This is an INTERVIEW FAVORITE — know the difference!
 
# # iloc = "integer location" — uses NUMBER positions (like a list)
# # Think: iloc uses INTEGERS, just like list[0], list[1], list[2]

# print("\n--- iloc: select by position number ---")
# print(df.iloc[0]) # first row

# print(df.iloc[2:5]) #2 to 4 rows 5 excluded

# print(df.iloc[0,0]) # "The Matrix" — [row_position, column_position]

# # loc = "label location" — uses INDEX LABELS and COLUMN NAMES
# # Think: loc uses LABELS (names you can read)
# print("\n--- loc: select by label/name ---")
# print(df.loc[0])  # Same as iloc[0] here because our index IS numbers

# print(df.loc[0:2, ["title", "rating"]])


# # Note: loc includes BOTH endpoints!
# # ^^^ This is different from iloc! loc[0:2] gives 3 rows (0,1,2)
# #     iloc[0:2] gives 2 rows (0,1) — just like Python slicing
 
# # INTERVIEW ANSWER for "loc vs iloc":
# # loc: label-based, inclusive of both endpoints, uses column names
# # iloc: integer-based, exclusive of end, uses position numbers
# # Example: df.loc[0:2] returns 3 rows, df.iloc[0:2] returns 2 rows

# # ============================================================================
# # PART 3: FILTERING — Finding specific data (most used operation!)
# # ============================================================================
# print("\n" + "=" * 60)
# print("PART 3: Filtering Rows")
# print("=" * 60)


# Filtering = "show me only the rows where THIS condition is true"
# It's like the WHERE clause in SQL!
 
# Step 1: Create a boolean mask (True/False for each row)

# print("\n--- Boolean mask: which movies are Sci-Fi? ---")
# mask = df["genre"] == "Sci-Fi"
# print(mask)

# scifi = df[mask]
# print(scifi)
# print(scifi[["title", "rating"]])

# # Shorthand — do it in one line (this is how you'll usually write it):
# print("\n--- Movies rated 8.8 or higher ---")

print(df[df["rating"] >= 8.8])
high_rated = df[df["rating"] >= 8.8]
print(high_rated[["title", "rating"]])

# Multiple conditions — use & (AND) and | (OR)
# IMPORTANT: each condition MUST be in parentheses!
print("\n--- Sci-Fi movies rated 8.7+ ---")

mask1 = (df["genre"] == "Sci-Fi") & (df["rating"] >= 8.8)
scifi_rated = df[mask1]

print(scifi_rated[["title", "genre", "rating"]])


print("\n--- Movies that are either Sci-Fi OR rated 9.0+ ---")
either = df[(df["genre"] == "Sci-Fi") | (df["rating"] >= 9.0)]
print(either[["title", "genre", "rating"]])
# In SQL: WHERE genre = 'Sci-Fi' OR rating >= 9.0

# .isin() — check if value is in a list (like SQL's IN clause)
print("\n--- Movies from 1994 or 1999 ---")

nineties = df[df["year"].isin([1994, 1999])]
print(nineties[["title", "year"]])

# String methods — .str lets you do text operations
print("\n--- Movies with 'The' in the title ---")
the_movies = df[df["title"].str.contains("The")]
print(the_movies[["title"]])
 
# Negation — use ~ (tilde) to flip True/False
print("\n--- Movies that are NOT Drama ---")
not_drama = df[~(df["genre"] == "Drama")]
print(not_drama[["title", "genre"]])


# ============================================================================
# PART 4: ADDING & MODIFYING COLUMNS — Computing new data
# ============================================================================

print("\n--- Adding profit column ---")
df["profit_millions"] = df["revenue_millions"] - df["budget_millions"]
print(df[["title", "budget_millions", "revenue_millions", "profit_millions"]])


# Add a calculated column
print("\n--- Adding ROI (Return on Investment) ---")
df["roi"] = (df["profit_millions"] / df["budget_millions"] * 100).round(1)
print(df[["title", "budget_millions", "profit_millions", "roi"]])
# ROI = how many % profit you made on your investment
# Pulp Fiction: spent $8M, made $206M profit → 2575% ROI!

df["tier"] = "Good" # Default is Good for all
df.loc[df["rating"] >= 8.8, "tier"] = "Great"
df.loc[df["rating"] >= 9.0, "tier"] = "Masterpiece"
print(df[["title", "rating", "tier"]])

print("\n--- Decade of each movie (using .apply) ---")

df["decade"] = df["year"].apply(lambda y : f"{(y//10) * 10}s")

# lambda y: ... → a mini function that takes year, returns decade string
# 1999 // 10 = 199 → 199 * 10 = 1990 → "1990s"
print(df[["title", "year", "decade"]])
