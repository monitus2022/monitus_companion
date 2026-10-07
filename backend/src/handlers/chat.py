import os
import json
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

from services.sessions_store import SessionStore
from utils.logger import get_logger

logger = get_logger("ChatHandler")

class ChatHandler:
    """Handler for managing chat interactions with Bedrock via AWS Lambda."""
    
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "ap-northeast-1")
        self.bedrock_client = boto3.client(
            "bedrock-runtime", 
            region_name=os.environ.get("BEDROCK_REGION", "us-east-1"), 
            config=Config(read_timeout=60)
        )
        self.default_model_id = os.environ.get(
            "DEFAULT_MODEL_ID", "us.amazon.nova-2-lite-v1:0"
        )
        self.session_store = SessionStore()

        # User Memory Table
        self.memory_table_name = os.environ.get("USER_MEMORY_TABLE", "monitus-user-memory")
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
        self.memory_table = self.dynamodb.Table(self.memory_table_name)

    def handle_request(self, event, context):
        logger.info("Processing incoming chat request...")

        http_method = event.get("requestContext", {}).get("http", {}).get("method", "POST")

        if http_method == "GET":
            params = event.get("queryStringParameters") or {}
            session_id = params.get("session_id", "default_session")
            
            logger.info(f"Fetching chat history for session_id: '{session_id}'")
            history = self.session_store.get_history(session_id=session_id)
            
            return self._build_response(200, {
                "status": "success",
                "session_id": session_id,
                "history": history
            })

        try:
            body = {}
            if isinstance(event.get("body"), str):
                body = json.loads(event["body"])
            elif isinstance(event.get("body"), dict):
                body = event["body"]

            user_input = body.get("message", "")
            model_id = body.get("model_id", self.default_model_id)
            session_id = body.get("session_id", "default_session")

            if not user_input:
                logger.warning("Empty message field in payload.")
                return self._build_response(400, {"error": "Message field cannot be empty."})

            logger.info(f"SessionId: '{session_id}' | ModelId: '{model_id}'")

            # 1. Fetch History
            history = self.session_store.get_history(session_id=session_id)
            history.append({"role": "user", "content": [{"text": user_input}]})

            # 2. Retrieve Persistent Facts
            user_facts = self._get_user_facts(user_id=session_id)
            system_text = "You are Monitus Companion, a helpful personal assistant."

            if user_facts:
                logger.info(f"Injecting {len(user_facts)} retrieved facts into system prompt.")
                facts_formatted = "\n".join([f"- [{f.get('category', 'general')}] {f['fact']}" for f in user_facts])
                system_text += f"\n\n[Known User Facts & Preferences]:\n{facts_formatted}"

            system_prompts = [{"text": system_text}]
            inference_config = {"maxTokens": 1000, "temperature": 0.7, "topP": 0.9}

            # 3. Invoke Model
            logger.info(f"Sending payload with {len(history)} messages to Bedrock...")
            response = self.bedrock_client.converse(
                modelId=model_id,
                messages=history,
                system=system_prompts,
                inferenceConfig=inference_config
            )

            assistant_reply = response["output"]["message"]["content"][0]["text"]
            logger.info("Received model response successfully.")

            # 4. Save History
            history.append({"role": "assistant", "content": [{"text": assistant_reply}]})
            self.session_store.save_history(session_id=session_id, messages=history)

            return self._build_response(200, {
                "status": "success",
                "session_id": session_id,
                "message": assistant_reply,
                "model_id": model_id
            })

        except ClientError as e:
            logger.exception("AWS ClientError caught during request handling")
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            return self._build_response(500, {"error": f"Bedrock ClientError [{error_code}]: {error_msg}"})
        except Exception as e:
            logger.exception("Unhandled exception caught during request handling")
            return self._build_response(500, {"error": f"An unexpected error occurred: {str(e)}"})

    def _get_user_facts(self, user_id: str) -> list:
        """Queries DynamoDB for all facts associated with user_id/session_id."""
        try:
            response = self.memory_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id)
            )
            return response.get("Items", [])
        except Exception as e:
            logger.warning(f"Failed to fetch user facts from memory table: {str(e)}")
            return []

    def _build_response(self, status_code, body_dict):
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps(body_dict)
        }

chat_service = ChatHandler()

def handler(event, context):
    return chat_service.handle_request(event, context)