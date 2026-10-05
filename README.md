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