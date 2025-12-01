import json
import os
import boto3

# Lambda function name - can be set via environment variable
# Default: client1-private_db_query
TARGET_FUNCTION = (
    os.environ.get("DB_QUERY_LAMBDA_FUNCTION") or
    os.environ.get("CLIENT1_PRIVATE_DB_QUERY") or
    "client1-private_db_query"  # Default Lambda function name
)


def database_query(query, params=None):
    """
    Execute a database query via Lambda function.
    
    Args:
        query: SQL query string
        params: Optional list of parameters for parameterized queries
    
    Returns:
        Query result (dict with 'data' and 'error' keys)
    """
    # TARGET_FUNCTION should always be set (has default value)
    if not TARGET_FUNCTION:
        raise RuntimeError(
            "Lambda function name not set. "
            "Set DB_QUERY_LAMBDA_FUNCTION or CLIENT1_PRIVATE_DB_QUERY environment variable, "
            "or the default 'client1-private_db_query' will be used."
        )
    
    client = boto3.client("lambda")
    payload = json.dumps({"query": query, "params": params or []})
    
    try:
        resp = client.invoke(
            FunctionName=TARGET_FUNCTION,
            InvocationType="RequestResponse",
            Payload=payload
        )
        
        # Read response payload (it's a stream)
        response_payload = resp["Payload"].read()
        result = json.loads(response_payload)
        
        # Handle Lambda function errors
        if "errorMessage" in result:
            raise RuntimeError(f"Lambda function error: {result['errorMessage']}")
        
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to invoke Lambda function {TARGET_FUNCTION}: {e}")