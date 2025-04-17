import pymongo
import psycopg2
import mysql.connector
import sqlite3
import json
import hashlib
import bcrypt

def get_db_connection(company):
    """Get a database connection based on company configuration"""
    db_type = company.db_type
    
    if company.connection_type == 'string' and company.connection_string:
        # Use connection string
        if db_type == 'mongodb':
            return get_mongodb_connection_string(company.connection_string)
        elif db_type == 'postgresql':
            return get_postgresql_connection_string(company.connection_string)
        elif db_type == 'mysql':
            return get_mysql_connection_string(company.connection_string)
        elif db_type == 'sqlite':
            return get_sqlite_connection_string(company.connection_string)
    else:
        # Use connection parameters
        if db_type == 'mongodb':
            return get_mongodb_connection(company)
        elif db_type == 'postgresql':
            return get_postgresql_connection(company)
        elif db_type == 'mysql':
            return get_mysql_connection(company)
        elif db_type == 'sqlite':
            return get_sqlite_connection(company)
    
    raise ValueError(f"Unsupported database type: {db_type}")

# MongoDB connections
def get_mongodb_connection(company):
    """Get MongoDB connection using parameters"""
    client = pymongo.MongoClient(
        host=company.db_host,
        port=company.db_port,
        username=company.db_user,
        password=company.db_password
    )
    return client[company.db_name]

def get_mongodb_connection_string(connection_string):
    """Get MongoDB connection using connection string"""
    client = pymongo.MongoClient(connection_string)
    # Extract database name from connection string
    db_name = connection_string.split('/')[-1].split('?')[0]
    return client[db_name]

# PostgreSQL connections
def get_postgresql_connection(company):
    """Get PostgreSQL connection using parameters"""
    conn = psycopg2.connect(
        host=company.db_host,
        port=company.db_port,
        database=company.db_name,
        user=company.db_user,
        password=company.db_password
    )
    return conn

def get_postgresql_connection_string(connection_string):
    """Get PostgreSQL connection using connection string"""
    return psycopg2.connect(connection_string)

# MySQL connections
def get_mysql_connection(company):
    """Get MySQL connection using parameters"""
    conn = mysql.connector.connect(
        host=company.db_host,
        port=company.db_port,
        database=company.db_name,
        user=company.db_user,
        password=company.db_password
    )
    return conn

def get_mysql_connection_string(connection_string):
    """Get MySQL connection using connection string"""
    return mysql.connector.connect(connection_string=connection_string)

# SQLite connections
def get_sqlite_connection(company):
    """Get SQLite connection using parameters"""
    conn = sqlite3.connect(company.db_name)
    return conn

def get_sqlite_connection_string(connection_string):
    """Get SQLite connection using connection string"""
    return sqlite3.connect(connection_string)

def table_exists(conn, table_name, db_type):
    """Check if a table exists in the database"""
    try:
        cursor = conn.cursor()
        
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            return cursor.fetchone()[0]
            
        elif db_type == 'mysql':
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = %s;
            """, (table_name,))
            return cursor.fetchone()[0] > 0
            
        elif db_type == 'sqlite':
            cursor.execute("""
                SELECT COUNT(*) 
                FROM sqlite_master 
                WHERE type='table' 
                AND name = ?;
            """, (table_name,))
            return cursor.fetchone()[0] > 0
            
        return False
    except Exception as e:
        print(f"Error checking if table exists: {str(e)}")
        return False

def create_table(conn, table_name, data, db_type):
    """Create a table based on the data structure"""
    try:
        cursor = conn.cursor()
        
        # Define column types based on data types
        columns = []
        for key, value in data.items():
            # Skip confirm_password field - we don't store it
            if key == 'confirm_password':
                continue
                
            if isinstance(value, int):
                columns.append((key, 'INTEGER'))
            elif isinstance(value, float):
                columns.append((key, 'FLOAT'))
            elif isinstance(value, bool):
                columns.append((key, 'BOOLEAN'))
            else:
                # Default to VARCHAR for all other types
                columns.append((key, 'VARCHAR(255)'))
        
        # Create SQL for table creation
        if db_type == 'postgresql':
            # Create column definitions
            column_defs = [f'"{col[0]}" {col[1]}' for col in columns]
            column_defs.insert(0, 'id SERIAL PRIMARY KEY')
            
            # Create table
            create_sql = f'CREATE TABLE "{table_name}" ({", ".join(column_defs)});'
            cursor.execute(create_sql)
            conn.commit()
            
        elif db_type == 'mysql':
            # Create column definitions
            column_defs = [f"`{col[0]}` {col[1]}" for col in columns]
            column_defs.insert(0, 'id INT AUTO_INCREMENT PRIMARY KEY')
            
            # Create table
            create_sql = f"CREATE TABLE `{table_name}` ({', '.join(column_defs)});"
            cursor.execute(create_sql)
            conn.commit()
            
        elif db_type == 'sqlite':
            # Create column definitions
            column_defs = [f'"{col[0]}" {col[1]}' for col in columns]
            column_defs.insert(0, 'id INTEGER PRIMARY KEY AUTOINCREMENT')
            
            # Create table
            create_sql = f'CREATE TABLE "{table_name}" ({", ".join(column_defs)});'
            cursor.execute(create_sql)
            conn.commit()
            
        return True
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        return False

def insert_data(company, data):
    """Insert data into the target table"""
    db_type = company.db_type
    table_name = company.target_table
    
    # Remove confirm_password from data before storing
    if 'confirm_password' in data:
        data = {k: v for k, v in data.items() if k != 'confirm_password'}
    
    # Get database connection
    conn = get_db_connection(company)
    
    try:
        if db_type == 'mongodb':
            # MongoDB doesn't need table creation - collections are created automatically
            collection = conn[table_name]
            result = collection.insert_one(data)
            return str(result.inserted_id)
        
        else:  # SQL databases (PostgreSQL, MySQL, SQLite)
            # Check if table exists
            if not table_exists(conn, table_name, db_type):
                # Create table if it doesn't exist
                if not create_table(conn, table_name, data, db_type):
                    raise Exception(f"Failed to create table {table_name}")
            
            cursor = conn.cursor()
            
            # Generate column names and placeholders
            columns = ', '.join([f'"{key}"' if db_type in ['postgresql', 'sqlite'] else f'`{key}`' for key in data.keys()])
            
            if db_type == 'postgresql':
                placeholders = ', '.join(['%s'] * len(data))
                query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders}) RETURNING id'
                cursor.execute(query, list(data.values()))
                inserted_id = cursor.fetchone()[0]
            
            elif db_type == 'mysql':
                placeholders = ', '.join(['%s'] * len(data))
                query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
                cursor.execute(query, list(data.values()))
                inserted_id = cursor.lastrowid
            
            elif db_type == 'sqlite':
                placeholders = ', '.join(['?'] * len(data))
                query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders})'
                cursor.execute(query, list(data.values()))
                inserted_id = cursor.lastrowid
            
            # Commit transaction
            conn.commit()
            
            return inserted_id
    
    finally:
        # Close connection
        if db_type != 'mongodb':
            conn.close()

def find_user(company, query):
    """Find a user in the database based on query parameters"""
    db_type = company.db_type
    table_name = company.target_table
    
    # Get database connection
    conn = get_db_connection(company)
    
    try:
        if db_type == 'mongodb':
            # MongoDB find
            collection = conn[table_name]
            return collection.find_one(query)
        
        elif db_type == 'postgresql':
            # Check if table exists
            if not table_exists(conn, table_name, db_type):
                return None
                
            # PostgreSQL find
            cursor = conn.cursor()
            
            # Generate WHERE clause
            where_clause = ' AND '.join([f"\"{key}\" = %s" for key in query.keys()])
            
            # Create SQL query
            sql_query = f"SELECT * FROM \"{table_name}\" WHERE {where_clause}"
            
            # Execute query
            cursor.execute(sql_query, list(query.values()))
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch result
            result = cursor.fetchone()
            
            if result:
                # Convert to dictionary
                return dict(zip(columns, result))
            return None
        
        elif db_type == 'mysql':
            # Check if table exists
            if not table_exists(conn, table_name, db_type):
                return None
                
            # MySQL find
            cursor = conn.cursor(dictionary=True)
            
            # Generate WHERE clause
            where_clause = ' AND '.join([f"`{key}` = %s" for key in query.keys()])
            
            # Create SQL query
            sql_query = f"SELECT * FROM `{table_name}` WHERE {where_clause}"
            
            # Execute query
            cursor.execute(sql_query, list(query.values()))
            
            # Fetch result
            return cursor.fetchone()
        
        elif db_type == 'sqlite':
            # Check if table exists
            if not table_exists(conn, table_name, db_type):
                return None
                
            # SQLite find
            cursor = conn.cursor()
            
            # Generate WHERE clause
            where_clause = ' AND '.join([f"\"{key}\" = ?" for key in query.keys()])
            
            # Create SQL query
            sql_query = f"SELECT * FROM \"{table_name}\" WHERE {where_clause}"
            
            # Execute query
            cursor.execute(sql_query, list(query.values()))
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch result
            result = cursor.fetchone()
            
            if result:
                # Convert to dictionary
                return dict(zip(columns, result))
            return None
    
    finally:
        # Close connection
        if db_type != 'mongodb':
            conn.close()

def update_user_password(company, user, new_password):
    """Update a user's password in the database"""
    db_type = company.db_type
    table_name = company.target_table
    
    # Hash the password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Get database connection
    conn = get_db_connection(company)
    
    try:
        if db_type == 'mongodb':
            # MongoDB update
            collection = conn[table_name]
            result = collection.update_one(
                {'_id': user['_id']},
                {'$set': {'password': hashed_password}}
            )
            return result.modified_count > 0
        
        elif db_type == 'postgresql':
            # Check if table exists
            if not table_exists(conn, table_name, db_type):
                return False
                
            # PostgreSQL update
            cursor = conn.cursor()
            
            # Create SQL query
            sql_query = f"UPDATE \"{table_name}\" SET \"password\" = %s WHERE id = %s"
            
            # Execute query
            cursor.execute(sql_query, [hashed_password, user['id']])
            
            # Commit transaction
            conn.commit()
            
            return cursor.rowcount > 0
        
        elif db_type == 'mysql':
            # Check if table exists
            if not table_exists(conn, table_name, db_type):
                return False
                
            # MySQL update
            cursor = conn.cursor()
            
            # Create SQL query
            sql_query = f"UPDATE `{table_name}` SET `password` = %s WHERE id = %s"
            
            # Execute query
            cursor.execute(sql_query, [hashed_password, user['id']])
            
            # Commit transaction
            conn.commit()
            
            return cursor.rowcount > 0
        
        elif db_type == 'sqlite':
            # Check if table exists
            if not table_exists(conn, table_name, db_type):
                return False
                
            # SQLite update
            cursor = conn.cursor()
            
            # Create SQL query
            sql_query = f"UPDATE \"{table_name}\" SET \"password\" = ? WHERE id = ?"
            
            # Execute query
            cursor.execute(sql_query, [hashed_password, user['id']])
            
            # Commit transaction
            conn.commit()
            
            return cursor.rowcount > 0
    
    finally:
        # Close connection
        if db_type != 'mongodb':
            conn.close()
