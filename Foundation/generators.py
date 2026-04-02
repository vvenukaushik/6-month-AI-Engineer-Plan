import csv
import random
import os
import sys
from typing import Generator

def create_sample_csv(filename: str, num_rows: int = 10000) -> str:
    categories = ["electronics", "books", "toys", "clothing", "food"]

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "product", "category", "price", "quantity"])

        for i in range(1, num_rows + 1):
            writer.writerow([
                i,
                f"Product_{i}",
                random.choice(categories),
                round(random.uniform(1.0,500.0), 2),
                random.randint(1,100),
            ])

    file_size = os.path.getsize(filename)
    print(f"Created {filename}: {num_rows: } rows, {file_size: } bytes")
    return filename


def load_all_into_memory(filename: str) -> list[dict]:

    results = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results


def read_csv_rows(filename: str) -> Generator[dict, None, None]:
    
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["price"] = float(row["price"])
            row["quantity"] = float(row["price"])
            yield row


def filter_by_category(rows: Generator, category: str) -> Generator[dict, None, None]:
    for row in rows:
        if row["category"] == category:
            yield row

def filter_by_price(rows: Generator, min_price: float, max_price: float) -> Generator[dict, None, None]:
    for row in rows:
        if min_price <= row["price"] <= max_price:
            yield row

def calculate_total(rows: Generator) -> Generator[dict, None, None]:
    for row in rows:
        row["total"] = round(row["price"] * row["quantity"], 2)
        yield row

def batch_rows(rows: Generator, batch_size: int = 100) -> Generator[list[dict], None, None]:
    batch = []
    for row in rows:
        batch.append(row)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

if __name__ == "__main__":
    csv_file = "sample_products.csv"
    create_sample_csv(csv_file, num_rows=10000)
    print()

    all_data = load_all_into_memory(csv_file)
    list_size = sys.getsizeof(all_data)

    print(f"List approach: {len(all_data):,} rows loaded, ~{list_size:,} bytes in memory")
    del all_data  # Free the memory


    gen = read_csv_rows(csv_file)
    gen_size = sys.getsizeof(gen)

    print(f" Generator approach: ~{gen_size} bytes in memory (just the generator object)")
    print(f"   That's {list_size // gen_size}x less memory!")
    print()

    print("Iterating over generator")

    row_gen = read_csv_rows(csv_file)
    for i in range(3):
        row = next(row_gen)
        print(f" Row {i+1}: {row}")
        print("remaining rows are not loaded yet")
    row_gen.close()
    # GENERATOR PIPELINE

    print("PIPELINE: Chaining generators (like an AI data pipeline)")

    pipe_line = calculate_total(
        filter_by_price(
            filter_by_category(
                read_csv_rows(csv_file),
                category="electronics"
            ),
            max_price=200.0,
            min_price=50.0
        )
    )

    count = 0
    total_revenue = 0.0
    for row in pipe_line:
        total_revenue += row["total"]
        count +=1
    print(f" Total: {count} electronics between $50-$200, revenue: ${total_revenue:,.2f}")
    print()

    print("BATCHING: Processing in chunks (like embedding API calls)")

    batched = batch_rows(read_csv_rows(csv_file), batch_size=500)

    batch_count = 0
    total_rows = 0
    for batch in batched:
        batch_count += 1
        total_rows +=len(batch)

    print(f"  ... processed {total_rows:,} rows in {batch_count} batches")
    print()

    os.remove(csv_file)

    print("🎓 KEY TAKEAWAYS:")
    print("   1. Generators use 'yield' instead of 'return' — they pause and resume")
    print("   2. Only ONE item is in memory at a time (critical for large datasets)")
    print("   3. Chain generators into pipelines: read → filter → transform → batch")
    print("   4. This is exactly how RAG document ingestion works (Month 3)")
    print("   5. Batch generators are how you call embedding APIs efficiently")