import os
import json
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

from services.sessions_store import SessionStore

class ChatHandler:
    """Handler for managing chat interactions with Bedrock via AWS Lambda."""
    
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "ap-northeast-1")
        # Use bedrock-runtime client for Converse API
        self.bedrock_client = boto3.client(
            "bedrock-runtime", 
            # region_name=self.region, 
            region_name="us-east-1", 
            config=Config(read_timeout=60)
            )
        self.default_model_id = os.environ.get(
            "DEFAULT_MODEL_ID", "us.amazon.nova-2-lite-v1:0"
        )
        self.session_store = SessionStore()

    def handle_request(self, event, context):
        """Main entry point for AWS Lambda invocations."""
        try:
            body = {}
            if isinstance(event.get("body"), str):
                body = json.loads(event["body"])
            elif isinstance(event.get("body"), dict):
                body = event["body"]

            user_input = body.get("message", "")
            model_id = body.get("model_id", self.default_model_id)

            if not user_input:
                return self._build_response(400, {"error": "Message field cannot be empty."})

            # For stateful session management provided by frontend
            session_id = body.get("session_id", "default_session")
            # DynamoDB history session management
            history = self.session_store.get_history(session_id=session_id)
            # Append the new user message to the history
            history.append(
                {
                    "role": "user",
                    "content": [{"text": user_input}]
                }
            )

            system_prompts = [
                {"text": "You are Monitus Companion, a helpful personal assistant."}
            ]

            inference_config = {
                "maxTokens": 1000,
                "temperature": 0.7,
                "topP": 0.9
            }

            # Call Bedrock Converse API
            response = self.bedrock_client.converse(
                modelId=model_id,
                messages=history,
                system=system_prompts,
                inferenceConfig=inference_config
            )

            assistant_reply = response["output"]["message"]["content"][0]["text"]

            # Append the assistant's reply to the history
            history.append({
                "role": "assistant",
                "content": [{"text": assistant_reply}]
            })
            self.session_store.save_history(session_id=session_id, messages=history)

            return self._build_response(200, {
                "status": "success",
                "session_id": session_id,
                "message": assistant_reply,
                "model_id": model_id
            })

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            return self._build_response(
                500, 
                {"error": f"Bedrock ClientError [{error_code}]: {error_msg}"}
                )
        except Exception as e:
            return self._build_response(
                500, 
                {"error": f"An unexpected error occurred: {str(e)}"}
                )

    def _build_response(self, status_code, body_dict):
        """Formats the HTTP response payload for API Gateway."""
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps(body_dict)
        }


# Instantiate service outside the handler for container reuse
chat_service = ChatHandler()

def handler(event, context):
    return chat_service.handle_request(event, context)