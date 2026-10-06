# monitus_companion

## Backend Setup

1. Install aws cli tools
```bash
brew install awscli
brew install aws-sam-cli
```

2. Build lambda function and deploy to AWS
```bash
sam build
sam deploy --guided
```
When prompted `Allow SAM CLI to create roles with the required permissions?`, select `Y`.

To get url from the deployed lambda function, run the following command:
```bash
aws cloudformation describe-stacks --stack-name monitus-companion --query "Stacks[0].Outputs[?OutputKey=='MonitusCompanionApi'].OutputValue" --output text
```

---

## Frontend Setup

1. Install dependencies
```bash
npm install
```

2. Create a `.env` file in the root directory and add the following environment variable:
```
VITE_CHAT_API_URL=https://<characters>.execute-api.<zone>.amazonaws.com
```

3. Start the development server
```bash
npm run dev
```