```markdown
# PostgreSQL Bulk Vacuum / Analyze Tool

This Python script connects to a PostgreSQL database and runs `VACUUM ANALYZE` on **all tables** within a predefined list of schemas. It is designed to help maintain database performance by reclaiming storage and updating planner statistics.

## Features

- ✅ Automatically discovers all base tables in each specified schema  
- ✅ Executes `VACUUM ANALYZE` on every table (autocommit mode required)  
- ✅ Provides per‑table progress output  
- ✅ Handles multiple schemas in a single run  
- ✅ Uses `psycopg2` with proper error handling and resource cleanup  

## Prerequisites

- Python 3.6+ installed  
- `psycopg2` (or `psycopg2-binary`) Python package  
- PostgreSQL database access (host, port, database, user, password)  
- **Permissions:** The database user must have the `VACUUM` privilege on all tables (typically superuser or table owner)  

## Installation

```bash
pip install psycopg2-binary
```

## Configuration

Edit the script and set your PostgreSQL connection details in the `DB_CONFIG` dictionary:

```python
DB_CONFIG = {
    'host': 'your_host',        # e.g., 'localhost' or IP
    'database': 'your_db',      # database name
    'user': 'your_user',        # role / username
    'password': 'your_password',
    'port': '5432'              # default PostgreSQL port
}
```

Optionally, modify the list of schemas to vacuum:

```python
lst = ['cdb', 'dwh', 'fuel', 'nfms', 'public', 'wfms', 'mmg', 'fep', 'mdms', 'spm', 'partition_sub']
```

## Usage

Run the script from the command line:

```bash
python vacuum_analyze.py
```

### Example Output

```
Found 12 tables in schema 'dwh'

Executing: VACUUM ANALYZE dwh.sales
✓ Completed: dwh.sales

Executing: VACUUM ANALYZE dwh.customers
✓ Completed: dwh.customers

...
```

## Important Notes

### 1. `autocommit` Mode
`VACUUM` and `VACUUM ANALYZE` cannot run inside a transaction block. The script therefore sets `conn.autocommit = True`. Any error that occurs will **not** roll back other vacuum operations.

### 2. Locking Behaviour
- Standard `VACUUM` (without `FULL`) acquires only a **share lock** and does not block normal reads/writes.  
- However, it still consumes I/O and CPU. Running it on many large tables consecutively may impact production performance – schedule it during low‑activity windows.

### 3. `VACUUM` vs `VACUUM FULL`
This script uses **plain `VACUUM ANALYZE`**. It marks dead tuples as reusable but **does not shrink the physical table file**. To release disk space to the operating system, you would need `VACUUM FULL`, which **locks the table exclusively**. That is intentionally not included here.

### 4. Statistics Update
`ANALYZE` updates the query planner statistics. This often improves execution plans for subsequent queries.

### 5. Error Handling
If a table does not exist or the user lacks permissions, the script prints the error and continues with the next table. The connection is closed cleanly at the end.

### 6. Performance Considerations
- Vacuuming thousands of tables can take a long time.  
- The script processes schemas sequentially, and tables within each schema alphabetically.  
- For large databases, consider using `pg_repack` or `vacuumdb` command‑line tool if more concurrency is needed.

## Customisation Ideas

- **Add a dry‑run mode** – list tables without executing `VACUUM`  
- **Add filter by table size** – skip tables below a certain size  
- **Add logging** – write results to a file instead of `stdout`  
- **Add concurrency** – use multiple connections to vacuum different schemas in parallel (use with caution)  

## Troubleshooting

| Issue | Possible solution |
|-------|-------------------|
| `psycopg2.OperationalError: VACUUM cannot run inside a transaction block` | Ensure `autocommit=True` is set before executing the vacuum command. |
| `Permission denied for relation …` | Grant the `VACUUM` privilege to the database user (`GRANT VACUUM ON TABLE … TO user;`) or run as superuser. |
| Script runs extremely slowly | Check system I/O and PostgreSQL `vacuum_cost_delay` settings. Consider breaking into smaller batches. |

## License

This script is provided “as is”, without warranty of any kind. It can be freely used, modified, and distributed.

---

**Author:** (Devikiran Panigrahi)  
**Maintainer:** devikiranpanigrahi@gmail.com  
**PostgreSQL version compatibility:** 9.6+
```
