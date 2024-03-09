import hashlib
import pyodbc

shards = {
    0: {
        'config': 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=db-sharderz-shard_2-1;DATABASE=Users;UID=sa;PWD=YourStrong!Passw0rd1',
    },
    1: {
        'config': 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=db-sharderz-shard_1-1;DATABASE=Users;UID=sa;PWD=YourStrong!Passw0rd2',
    }
}

def get_shard_key(guid : str) :
    guid_hash_key = hashlib.sha256(guid.encode()).hexdigest()
    shard_key = int(guid_hash_key[0], 16) % len(shards)
    return shards[shard_key]


def get_connection(guid : str):
    shard_key = get_shard_key(guid)
    config = shards[shard_key]['config']
    conn = pyodbc.connect(config)
    return conn


def execute(guid : str, query : str, parameters = None):
    
    conn = get_connection(guid)
    cursor = conn.cursor()

    if parameters:
        cursor.execute(query, parameters)
    else:
        cursor.execute(query)

    if query.strip().lower().startswith('select'):
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    else:
        conn.commit()
        cursor.close()
        conn.close()

    
def execute_query_on_all_shards(query, parameters=None):
    all_results = []
    for shard_key in shards.keys():
        config = shards[shard_key]['config']
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        
        if query.strip().lower().startswith('select'):
            results = cursor.fetchall()
            all_results.extend(results)
        
        cursor.close()
        conn.close()
    
    return all_results



def insert_data(guid, table_name, data):
   
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    execute(guid, query, tuple(data.values()))
