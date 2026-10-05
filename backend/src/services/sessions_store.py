import os
import time
import boto3
from botocore.exceptions import ClientError

class SessionStore:
    """Encapsulates all DynamoDB operations for chat session history."""

    def __init__(self, table_name=None, region_name=None, max_history_turns=10, ttl_hours=24):
        self.table_name = table_name or os.environ.get("SESSION_TABLE", "monitus-chat-sessions")
        self.region_name = region_name or os.environ.get("AWS_REGION", "ap-northeast-1")
        self.max_history_turns = max_history_turns
        self.ttl_seconds = ttl_hours * 3600
        
        # Initialize DynamoDB resource once during class instantiation
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region_name)
        self.table = self.dynamodb.Table(self.table_name)

    def get_history(self, session_id: str) -> list:
        """Fetch past messages array for a given session ID."""
        try:
            response = self.table.get_item(Key={"session_id": session_id})
            return response.get("Item", {}).get("messages", [])
        except ClientError as e:
            print(f"[SessionStore] AWS Error fetching history for '{session_id}': {e}")
            return []
        except Exception as e:
            print(f"[SessionStore] Unexpected error fetching history for '{session_id}': {e}")
            return []

    def save_history(self, session_id: str, messages: list) -> bool:
        """Save updated messages array with sliding window trimming and TTL timestamp."""
        try:
            # Unix epoch timestamp for TTL expiry
            ttl_timestamp = int(time.time()) + self.ttl_seconds
            
            # Sliding window: keep only the most recent N turns
            trimmed_messages = messages[-self.max_history_turns:]

            self.table.put_item(
                Item={
                    "session_id": session_id,
                    "messages": trimmed_messages,
                    "ttl": ttl_timestamp
                }
            )
            return True
        except ClientError as e:
            print(f"[SessionStore] AWS Error saving session '{session_id}': {e}")
            return False
        except Exception as e:
            print(f"[SessionStore] Unexpected error saving session '{session_id}': {e}")
            return False