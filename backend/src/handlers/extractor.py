import os
import json
import hashlib
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

from utils.logger import get_logger

logger = get_logger("ExtractorHandler")

EXTRACTION_SYSTEM_PROMPT = (
    "You are a memory extraction sub-agent. Analyze the user's message and identify any long-term facts, "
    "core preferences, technical stack choices, or personal details worth remembering.\n"
    "Rules:\n"
    "1. ONLY extract clear, enduring facts about the user (e.g., programming languages, project goals, hardware, daily routines).\n"
    "2. Ignore transient conversational chatter, greetings, or questions directed at the assistant.\n"
    "3. Return strict JSON matching this exact structure:\n"
    '{\n  "facts": [\n    {"category": "tech_stack|preference|personal", "fact": "Concise fact description"}\n  ]\n}\n'
    '4. If NO long-term facts exist in the message, return exactly: {"facts": []}'
)


class ExtractorHandler:
    """Handler for extracting user facts from DynamoDB Stream events via Bedrock."""

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
        self.memory_table_name = os.environ.get("USER_MEMORY_TABLE", "monitus-user-memory")
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
        self.memory_table = self.dynamodb.Table(self.memory_table_name)

    def handle_request(self, event, context):
        """Main entry point for processing DynamoDB Stream batches."""
        records = event.get("Records", [])
        logger.info(f"Processing batch of {len(records)} stream record(s)...")

        processed_count = 0
        extracted_facts_count = 0

        for record in records:
            # Process strictly new database writes
            if record.get("eventName") != "INSERT" and record.get("eventName") != "MODIFY":
                continue

            try:
                new_image = record.get("dynamodb", {}).get("NewImage", {})
                user_text = self._extract_user_text_from_image(new_image)

                if not user_text:
                    logger.debug("No new user text found in stream record. Skipping.")
                    continue

                logger.info(f"Analyzing message for memory extraction: '{user_text[:50]}...'")

                # Single-pass LLM extraction
                facts = self._extract_facts_with_llm(user_text)

                if facts:
                    session_id = new_image.get("session_id", {}).get("S", "default_user")
                    self._save_facts(user_id=session_id, facts=facts)
                    extracted_facts_count += len(facts)
                    logger.info(f"Saved {len(facts)} fact(s) for user/session '{session_id}'.")
                else:
                    logger.info("No long-term facts detected in message.")

                processed_count += 1

            except ClientError as e:
                logger.exception("AWS ClientError encountered while processing stream record.")
            except Exception as e:
                logger.exception("Unexpected error processing stream record.")

        return {
            "status": "success",
            "processed_records": processed_count,
            "extracted_facts": extracted_facts_count
        }

    def _extract_facts_with_llm(self, user_text: str) -> list:
        """Invokes Bedrock Converse API with zero temperature to evaluate facts."""
        messages = [
            {
                "role": "user",
                "content": [{"text": f"User message to analyze: \"{user_text}\""}]
            }
        ]
        system_prompts = [{"text": EXTRACTION_SYSTEM_PROMPT}]
        inference_config = {"temperature": 0.0, "maxTokens": 256}

        response = self.bedrock_client.converse(
            modelId=self.default_model_id,
            messages=messages,
            system=system_prompts,
            inferenceConfig=inference_config
        )

        output_text = response["output"]["message"]["content"][0]["text"]

        try:
            data = json.loads(output_text)
            return data.get("facts", [])
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from Bedrock output: {output_text}")
            return []

    def _save_facts(self, user_id: str, facts: list):
        """Persists extracted facts to the monitus-user-memory DynamoDB table."""
        with self.memory_table.batch_writer() as batch:
            for item in facts:
                fact_text = item.get("fact", "")
                if not fact_text:
                    continue

                # Create deterministic hash-based memory_id to avoid duplicate writes
                fact_hash = hashlib.sha256(fact_text.lower().encode("utf-8")).hexdigest()[:12]
                memory_id = f"fact#{fact_hash}"

                batch.put_item(
                    Item={
                        "user_id": user_id,
                        "memory_id": memory_id,
                        "category": item.get("category", "general"),
                        "fact": fact_text
                    }
                )

    def _extract_user_text_from_image(self, new_image: dict) -> str:
        """Parses DynamoDB stream image to extract the latest user input."""
        # Case 1: Session store saves array of messages under "messages"
        if "messages" in new_image and "L" in new_image["messages"]:
            msg_list = new_image["messages"]["L"]
            for msg in reversed(msg_list):
                msg_map = msg.get("M", {})
                role = msg_map.get("role", {}).get("S", "")
                if role == "user":
                    content = msg_map.get("content", {}).get("L", [])
                    if content and "M" in content[0]:
                        return content[0]["M"].get("text", {}).get("S", "")