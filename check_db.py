import sqlite3

conn = sqlite3.connect('data/database/college.db')
cursor = conn.cursor()

print("=" * 60)
print("DATABASE CONNECTION STATUS")
print("=" * 60)

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\n✅ Database connected successfully!")
print(f"Location: data/database/college.db")
print(f"\nTables found: {len(tables)}")

for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  - {table_name}: {count} rows")

# Check specific important tables
required_tables = ['students', 'courses', 'enrollments', 'attendance', 
                   'faculty', 'fees', 'exams', 'conversation_history']

print(f"\nRequired tables check:")
for req_table in required_tables:
    exists = any(t[0] == req_table for t in tables)
    status = "✅" if exists else "❌"
    print(f"  {status} {req_table}")

conn.close()
print("\n" + "=" * 60)
