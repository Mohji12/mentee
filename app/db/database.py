from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
import os
import pymysql

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, will use system environment variables
    pass

# Get DATABASE_URL from environment variable, with project default fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://adminuser:Mentee123%40@52.90.192.59:3306/psychometric"
)

# Parse database URL for diagnostics
def get_db_info():
    """Extract database connection info for diagnostics"""
    try:
        # Remove the mysql+pymysql:// prefix
        url_part = DATABASE_URL.replace("mysql+pymysql://", "")
        if "@" in url_part:
            creds_part, server_part = url_part.split("@", 1)
            if ":" in server_part:
                server, db = server_part.rsplit("/", 1) if "/" in server_part else (server_part, "")
                host, port = server.split(":") if ":" in server else (server, "3306")
                return {"host": host, "port": port, "database": db}
    except:
        pass
    return {"host": "unknown", "port": "unknown", "database": "unknown"}

# Create engine with connection pooling and error handling
# Reduced pool_recycle to prevent stale connections (AWS RDS often has shorter wait_timeout)
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_pre_ping=True,  # Verify connections before using (critical for detecting stale connections)
    pool_recycle=1800,   # Recycle connections after 30 minutes (prevent stale connections)
    pool_size=5,         # Number of connections to maintain
    max_overflow=10,     # Maximum overflow connections
    echo=False,          # Set to True for SQL query logging
    connect_args={
        "connect_timeout": 30,  # Connection timeout
        "read_timeout": 60,     # Increased read timeout for long queries
        "write_timeout": 60,     # Increased write timeout for long operations
        "charset": "utf8mb4",
        "autocommit": False
    }
)

# Add event listener to log connection events and handle errors
@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when a connection is checked out from the pool (only if DEBUG is set)."""
    if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
        print(f"Database connection checked out: {id(dbapi_conn)}")

@event.listens_for(engine, "invalidate")
def handle_invalidate(dbapi_conn, connection_record, exception):
    """Handle connection invalidation with better error messages"""
    db_info = get_db_info()
    error_msg = (
        f"\n{'='*60}\n"
        f"Database Connection Error\n"
        f"{'='*60}\n"
        f"Host: {db_info['host']}\n"
        f"Port: {db_info['port']}\n"
        f"Database: {db_info['database']}\n"
        f"Error Type: {type(exception).__name__ if exception else 'Unknown'}\n"
        f"Error Message: {str(exception) if exception else 'Connection invalidated'}\n"
        f"{'='*60}\n"
        f"Possible causes:\n"
        f"  1. Database server is not running or unreachable\n"
        f"  2. Network connectivity issues or firewall blocking\n"
        f"  3. Incorrect credentials or database name\n"
        f"  4. AWS RDS security group not allowing your IP\n"
        f"  5. RDS instance might be stopped\n"
        f"  6. Connection timeout or idle connection closed by server\n"
        f"{'='*60}\n"
    )
    print(error_msg)

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Set connection-level settings to prevent premature disconnection"""
    # Set session variables to keep connections alive longer
    # This helps prevent "Lost connection" errors
    try:
        cursor = dbapi_conn.cursor()
        # Set wait_timeout to match our pool_recycle (in seconds)
        cursor.execute("SET SESSION wait_timeout = 1800")  # 30 minutes
        cursor.execute("SET SESSION interactive_timeout = 1800")  # 30 minutes
        cursor.close()
    except Exception as e:
        # If we can't set these, log but don't fail
        if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
            print(f"Warning: Could not set connection timeout settings: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session with improved error handling and retry logic for connection loss"""
    db = None
    max_retries = 2
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            db = SessionLocal()
            # Test the connection by executing a simple query
            try:
                db.execute(text("SELECT 1"))
            except (SQLAlchemyError, DisconnectionError, pymysql.err.InterfaceError, pymysql.err.OperationalError) as conn_error:
                # Check if it's a connection loss error (2013) that we can retry
                error_code = None
                if hasattr(conn_error, 'orig') and hasattr(conn_error.orig, 'args'):
                    error_code = conn_error.orig.args[0] if conn_error.orig.args else None
                
                # Retry on connection loss errors (2013) or interface errors
                if retry_count < max_retries and (
                    error_code == 2013 or  # Lost connection to MySQL server
                    isinstance(conn_error, (DisconnectionError, pymysql.err.InterfaceError)) or
                    'Lost connection' in str(conn_error) or
                    'forcibly closed' in str(conn_error)
                ):
                    retry_count += 1
                    if db:
                        try:
                            db.close()
                        except:
                            pass
                    db = None
                    # Invalidate the connection pool to force new connections
                    engine.dispose()
                    continue  # Retry
                
                # Provide detailed error information for non-retryable errors
                db_info = get_db_info()
                error_msg = (
                    f"\n{'='*60}\n"
                    f"Database Connection Failed\n"
                    f"{'='*60}\n"
                    f"Error Type: {type(conn_error).__name__}\n"
                    f"Error Message: {str(conn_error)}\n"
                    f"Host: {db_info['host']}\n"
                    f"Port: {db_info['port']}\n"
                    f"Database: {db_info['database']}\n"
                    f"{'='*60}\n"
                    f"Troubleshooting Steps:\n"
                    f"  1. Verify the RDS instance is running in AWS Console\n"
                    f"  2. Check security group allows connections from your IP\n"
                    f"  3. Verify network connectivity: ping {db_info['host']}\n"
                    f"  4. Test connection manually: mysql -h {db_info['host']} -P {db_info['port']} -u admin -p\n"
                    f"  5. Check if DATABASE_URL environment variable is set correctly\n"
                    f"{'='*60}\n"
                )
                print(error_msg)
                import traceback
                if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
                    print(f"Full traceback:\n{traceback.format_exc()}")
                if db:
                    try:
                        db.rollback()
                    except:
                        pass
                raise
            
            # Connection successful, yield the session
            try:
                yield db
            finally:
                # Always close the session when done
                if db:
                    try:
                        db.close()
                    except:
                        pass
            return  # Success, exit retry loop
            
        except (SQLAlchemyError, DisconnectionError, pymysql.err.InterfaceError, pymysql.err.OperationalError) as db_error:
            # Check if it's a connection loss error that we can retry
            error_code = None
            if hasattr(db_error, 'orig') and hasattr(db_error.orig, 'args'):
                error_code = db_error.orig.args[0] if db_error.orig.args else None
            
            # Retry on connection loss errors during operation
            if retry_count < max_retries and (
                error_code == 2013 or  # Lost connection to MySQL server
                isinstance(db_error, (DisconnectionError, pymysql.err.InterfaceError)) or
                'Lost connection' in str(db_error) or
                'forcibly closed' in str(db_error)
            ):
                retry_count += 1
                if db:
                    try:
                        db.rollback()
                        db.close()
                    except:
                        pass
                db = None
                # Invalidate the connection pool to force new connections
                engine.dispose()
                continue  # Retry
            
            # Non-retryable error or max retries reached
            error_msg = f"Database error during operation: {type(db_error).__name__}: {str(db_error)}"
            print(error_msg)
            import traceback
            if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
                print(f"Full traceback:\n{traceback.format_exc()}")
            if db:
                try:
                    db.rollback()
                    db.close()
                except:
                    pass
            raise
    
    # If we get here, all retries failed
    if db:
        try:
            db.close()
        except:
            pass
    raise Exception("Failed to establish database connection after retries")