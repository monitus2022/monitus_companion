# Workplan

### Stage 1: Infrastructure as Code & Core Chat MVP

**Estimated Time: Week 1 | Target: Live Web Chat at `companion.monitus.org**`


Establish the serverless foundation, automated deployment pipeline, and baseline chat capabilities using the AWS Bedrock Converse API.

* **Repository & IaC Setup**: Initialize the Git repository with **AWS SAM** (`template.yaml`) and configure environment parameters for seamless multi-stage deployments.


* **Core Agent Lambda**: Write `src/handlers/chat.py` in Python 3.12 using `boto3` to interact with the **Amazon Bedrock Converse API** (`us.amazon.nova-2-lite-v1:0`).


* **Short-Term Session Store**: Provision an **Amazon DynamoDB** table with `session_id` (partition key) and a 48-hour Time-to-Live (TTL) attribute to store sliding-window conversation turns.


* **Frontend Deployment**: Build a light, modern Vite + React chat interface and deploy to **Cloudflare Pages**, binding custom domain routing (`companion.monitus.org`).



---

### Stage 2: 3-Tier Persistent Memory Engine

**Estimated Time: Week 2 | Target: Contextual Fact Memory Across Sessions**


Upgrade the assistant from a simple chatbot into a persistent agent that extracts and recalls user facts, preferences, and historical interactions over time.

* **Tier 1 (Working Memory)**: Maintain the 48-hour DynamoDB chat buffer built in Stage 1.


* **Tier 2 (Semantic Memory)**: Enable **DynamoDB Streams** on the session table. Attach an asynchronous **Extractor Lambda** that invokes Bedrock after every conversation to extract and deduplicate key facts into a `UserMemory` table.


* **Tier 3 (Episodic Memory)**: Generate vector embeddings for past conversation summaries using **Amazon Titan Text Embeddings V2** (`amazon.titan-embed-text-v2:0`). Perform in-memory cosine similarity search directly inside Lambda to eliminate dedicated vector database costs.


* **Context Injector**: Update the main chat Lambda to retrieve semantic facts and relevant past episodes before constructing the final prompt payload for Bedrock.



---

### Stage 3: Hybrid Voice Engine & Proactive Reminders

**Estimated Time: Week 3 | Target: On-Device Neural Voice & Autonomous Audio Alerts**


Combine client-side WebGPU/WASM neural voice execution for $0-cost interactive chat with server-side scheduled push notifications.

* **Client-Side Neural TTS (Primary Chat Voice)**: Integrate **`kokoro-js`** into the React frontend to execute quantized 82M-parameter neural speech models (`Kokoro-82M-v1.0-ONNX`) directly in the user's browser via **WebAssembly/WebGPU**. Provides studio-quality voice generation with 0ms backend latency, complete user privacy, and **$0.00 cloud compute cost**.
* **Browser Audio Caching**: Cache model weights locally in browser `IndexedDB` on initial load, enabling instant offline playback for subsequent chat turns.
* **Tool Calling Schema**: Define a `schedule_reminder` tool schema inside Bedrock's `toolConfig` parameter.


* **EventBridge Scheduler Integration**: When Bedrock executes the tool call, the Lambda handler invokes the AWS SDK `CreateSchedule` API in **AWS EventBridge Scheduler**.


* **Proactive Cloud Voice (Secondary Push Alerts)**: Trigger an EventBridge target Lambda that calls **Amazon Polly Neural TTS** (`SynthesizeSpeech` with `Joanna-Neural` or `Ruth-Neural`) to synthesize MP3 audio streams strictly for background scheduled alerts.


* **Web Push Delivery**: Configure Web Push VAPID keys on Cloudflare Pages (or a Discord/Telegram Webhook fallback) to deliver proactive spoken audio notifications directly to user devices.



---

### Stage 4: Developer Co-Pilot & GitHub Webhooks

**Estimated Time: Week 4 | Target: Real-Time Git Commit Code Reviews**


Transform *Monitus Companion* into an active developer co-pilot that inspects code pushes to your GitHub repositories in real time.

* **Webhook Receiver Endpoint**: Expose `POST /webhooks/github` on AWS API Gateway backed by a dedicated Ingestion Lambda.


* **Security & HMAC Verification**: Validate incoming `X-Hub-Signature-256` headers using a shared secret stored in **AWS Systems Manager (SSM) Parameter Store**.


* **Diff Fetching & Filtering**: Extract commit hashes from the payload, fetch modified file unified diffs via the GitHub REST API, and strip out non-code assets or lockfiles.


* **Bedrock Code Review**: Prompt Bedrock Nova Lite / Haiku to generate concise (<200 words) architectural feedback, edge-case warnings, and security critiques based on the diff and stored memory coding preferences.


* **Proactive Delivery**: Route the generated review to the Stage 3 Notification Engine to trigger an immediate text alert and spoken audio summary.



---

### Stage 5: Production Hardening, Observability & Polish

**Estimated Time: Week 5 | Target: Production Release & Enterprise Guardrails**


Apply enterprise security controls, cost monitoring, and production-grade documentation.

* **Amazon Bedrock Guardrails**: Attach guardrail policies to mask sensitive PII (API keys, emails) and enforce content safety filters.


* **IAM Least Privilege**: Audit and tighten IAM policy statements across all Lambda execution roles.


* **Cost Observability**: Configure AWS Budgets and CloudWatch Cost Anomaly alarms set at a **$2.00 USD/month** threshold.


* **MCP Server Endpoint**: Expose core backend tools through a Model Context Protocol (MCP) server wrapper on Lambda for local IDE integration (Cursor, VS Code).


* **Open-Source Release**: Publish a clean GitHub repository containing architecture diagrams, automated CI/CD workflows, live web links (`companion.monitus.org`), and deployment docs.