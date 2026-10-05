# Workplan

1. **Stage 1: Infrastructure as Code & Core Chat MVP:** Estimated Time: Week 1 | Target: Live Web Chat at app.monitus.org.
Establish the serverless foundation, automated deployment pipeline, and baseline chat capabilities using the AWS Bedrock Converse API.

* **Repository & IaC Setup**: Initialize the Git repository with **AWS SAM** (`template.yaml`) and create a GitHub Actions deployment workflow (`.github/workflows/deploy.yml`) with IAM credentials stored in GitHub Secrets.
* **Core Agent Lambda**: Write `src/app.py` in Python 3.12 using `boto3` to call the **Amazon Bedrock Converse API** (`amazon.nova-lite-v1:0` or `anthropic.claude-3-5-haiku`).
* **Short-Term Session Store**: Provision an **Amazon DynamoDB** table with `SessionId` (partition key) and a 48-hour Time-to-Live (TTL) attribute to store the last 10 conversation turns.
* **Frontend Deployment**: Build a light, modern chat UI and deploy to **Cloudflare Pages**, binding your custom domain (`app.monitus.org`).
* **MLA-C02 Competencies**: Infrastructure as Code (SAM/CloudFormation), Bedrock Converse API parameterization, serverless API integration.


2. **Stage 2: 3-Tier Persistent Memory Engine:** Estimated Time: Week 2 | Target: Contextual Fact Memory Across Sessions.
Upgrade the assistant from a simple chatbot into a persistent agent that learns and recalls user facts, preferences, and historical interactions over time.

* **Tier 1 (Working Memory)**: Maintain the 48-hour DynamoDB chat buffer built in Stage 1.
* **Tier 2 (Semantic Memory)**: Enable **DynamoDB Streams** on the session table. Attach an asynchronous **Extractor Lambda** that invokes Bedrock after every conversation to extract and deduplicate key facts into a `UserMemory` table.
* **Tier 3 (Episodic Memory)**: Generate vector embeddings for past conversation summaries using **Amazon Titan Text Embeddings V2** (`amazon.titan-embed-text-v2:0`). Store vector arrays in DynamoDB and perform in-memory cosine similarity search inside Lambda (eliminating dedicated vector database costs).
* **Context Injector**: Update the main chat Lambda to retrieve semantic facts and relevant past episodes before constructing the final prompt payload for Bedrock.
* **MLA-C02 Competencies**: Vector embeddings (Titan V2), DynamoDB Streams event-driven pattern, RAG context window management.


3. **Stage 3: Proactive Voice & Notification Engine:** Estimated Time: Week 3 | Target: Spoken Audio Push Notifications.
Enable the assistant to autonomously schedule actions and reach out to you with neural voice messages without waiting for a user prompt.

* **Tool Calling Config**: Define a `schedule_reminder` tool schema inside Bedrock's `toolConfig` parameter.
* **EventBridge Scheduler Integration**: When Bedrock executes the tool call, the Lambda handler invokes the AWS SDK `CreateSchedule` API in **AWS EventBridge Scheduler**.
* **Notification Dispatcher Lambda**: Create an execution target Lambda triggered by EventBridge when a timer fires.
* **Amazon Polly Neural TTS**: Pass the reminder text to Amazon Polly (`SynthesizeSpeech` API) using a Neural voice profile (`Joanna-Neural` / `Matthew-Neural`) to produce an MP3 audio stream.
* **Web Push Delivery**: Configure Web Push VAPID keys on Cloudflare Pages (or a Telegram/Discord Webhook fallback) to deliver proactive audio push alerts directly to your devices.
* **MLA-C02 Competencies**: FM tool calling & function orchestration, EventBridge event scheduling, Amazon Polly integration.


4. **Stage 4: Developer Co-Pilot & GitHub Webhooks:** Estimated Time: Week 4 | Target: Real-Time Git Commit Code Reviews.
Transform *Monitus Companion* into an active developer co-pilot that inspects code pushes to your GitHub repositories in real time.

* **Webhook Receiver Endpoint**: Expose `POST /webhooks/github` on AWS API Gateway backed by a dedicated Ingestion Lambda.
* **Security & HMAC Verification**: Validate incoming `X-Hub-Signature-256` headers using a shared secret stored in **AWS Systems Manager (SSM) Parameter Store**.
* **Diff Fetching & Filtering**: Extract commit hashes from the payload, fetch modified file unified diffs via the GitHub REST API, and strip out non-code assets or lockfiles.
* **Bedrock Code Review**: Prompt Bedrock Nova Lite / Haiku to generate concise (<200 words) architectural feedback, edge-case warnings, and security critiques based on the diff and your stored memory coding preferences.
* **Proactive Delivery**: Route the generated review to the Stage 3 Notification Engine to trigger an immediate text alert and spoken Polly audio summary.
* **MLA-C02 Competencies**: Event-driven architecture, SSM secret management, prompt engineering for code analysis.


5. **Stage 5: Production Hardening, Observability & Polish:** Estimated Time: Week 5 | Target: Portfolio Launch & Enterprise Guardrails.
Apply enterprise security controls, cost monitoring, and create portfolio assets to highlight on your resume and in job interviews.

* **Amazon Bedrock Guardrails**: Attach guardrail policies to mask sensitive PII (API keys, emails) and enforce content safety filters.
* **IAM Least Privilege**: Audit and tighten IAM policy statements across all Lambda execution roles.
* **Cost Observability**: Configure AWS Budgets and CloudWatch Cost Anomaly alarms set at a **$2.00 USD/month** threshold.
* **(Optional) MCP Server Endpoint**: Expose your core backend tools through a `FastMCP` server wrapper on Lambda for local IDE access via Cursor or Claude Desktop.
* **Portfolio & Resume Launch**: Publish an open-source GitHub repository containing a high-quality `README.md`, system architecture diagram, live web link (`monitus.org`), and sample audio push demo.
* **MLA-C02 Competencies**: AI safety & governance, IAM security best practices, CloudWatch telemetry & token usage tracking.