import os
import time
import boto3
from botocore.exceptions import ClientError

from utils.logger import get_logger

logger = get_logger("SessionStore")

class SessionStore:
    """Encapsulates all DynamoDB operations for chat session history."""

    def __init__(self, table_name=None, region_name=None, max_history_turns=10, ttl_hours=24):
        self.table_name = table_name or os.environ.get("SESSIONS_TABLE", "monitus-chat-sessions")
        self.region_name = region_name or os.environ.get("AWS_REGION", "ap-northeast-1")
        self.max_history_turns = max_history_turns
        self.ttl_seconds = ttl_hours * 3600
        
        logger.info(f"Initializing SessionStore. Table: '{self.table_name}' | Region: '{self.region_name}'")
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region_name)
        self.table = self.dynamodb.Table(self.table_name)

    def get_history(self, session_id: str) -> list:
        try:
            logger.info(f"Fetching history for session_id: '{session_id}'")
            response = self.table.get_item(Key={"session_id": session_id})
            messages = response.get("Item", {}).get("messages", [])
            logger.info(f"Retrieved {len(messages)} messages for session_id: '{session_id}'")
            return messages
        except ClientError as e:
            logger.exception(f"AWS ClientError fetching session '{session_id}'")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error fetching session '{session_id}'")
            return []

    def save_history(self, session_id: str, messages: list) -> bool:
        try:
            ttl_timestamp = int(time.time()) + self.ttl_seconds
            trimmed_messages = messages[-self.max_history_turns:]

            logger.info(f"Saving {len(trimmed_messages)} messages to session_id: '{session_id}'")
            self.table.put_item(
                Item={
                    "session_id": session_id,
                    "messages": trimmed_messages,
                    "ttl": ttl_timestamp
                }
            )
            logger.info(f"Successfully saved state for session_id: '{session_id}'")
            return True
        except ClientError as e:
            logger.exception(f"AWS ClientError saving session '{session_id}'")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error saving session '{session_id}'")
            raise e