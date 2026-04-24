import psycopg2
from psycopg2 import sql

# Database connection parameters
DB_CONFIG = {
    'host': '10.160.196.60',
    'database': 'adnoc_tnd',
    'user': 'postgres',
    'password': 'Fluent@123',
    'port': '5432'
}


def vacuum_analyze_tables(schema):
    """
    Execute VACUUM ANALYZE on all tables in specified schema.
    Note: VACUUM cannot run inside a transaction, so we use autocommit.
    """
    conn = None
    try:
        # Connect with autocommit enabled (required for VACUUM)
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True  # Critical: VACUUM cannot run in transaction
        
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, (schema,))
        
        tables = cursor.fetchall()
        print(f"Found {len(tables)} tables in schema '{schema}'\n")
        
        # Execute VACUUM ANALYZE for each table
        for table_schema, table_name in tables:
            vacuum_cmd = sql.SQL("VACUUM ANALYZE {}.{}").format(
                sql.Identifier(table_schema),
                sql.Identifier(table_name)
            )
            
            print(f"Executing: {vacuum_cmd.as_string(conn)}")
            cursor.execute(vacuum_cmd)
            print(f"✓ Completed: {table_schema}.{table_name}\n")
            
        print("All tables processed successfully!")
        
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    lst = ['cdb','dwh','fuel','nfms','public','wfms','mmg','fep','mdms','spm','partition_sub']
    for schema in lst:
        vacuum_analyze_tables(schema)

