# AI Digital Twin

[![Live Website](https://img.shields.io/badge/Live_Website-6c63ff?logo=rocket&logoColor=white&labelColor=5a52d3)](http://projects.kaushikpaul.co.in/ai-chat)

An AI-powered digital twin that represents Kaushik Paul in conversations. Users can chat with the twin to learn about career background, skills, and experience via a clean Next.js frontend and a FastAPI backend.

> **Upgrade Note**  
> This project is an upgraded, production-ready evolution of my earlier **Career Conversation** assistant: [Career-Conversation](https://github.com/Kaushik-Paul/Career-Conversation).

- **Live Demo**: http://projects.kaushikpaul.co.in/ai-chat
- **Backend**: FastAPI on AWS Lambda (via API Gateway + Terraform)
- **Frontend**: Next.js static export on S3 + CloudFront
- **AI Providers**:
  - Main branch: OpenRouter models
  - AWS Bedrock branch: Amazon Bedrock (e.g., `apac.amazon.nova-lite-v1:0`)

---

## Features
- **Chat with a Digital Twin** using `/chat` endpoint and persistent session memory
- **Two AI integration modes**:
  - OpenRouter (default on `main`)
  - Amazon Bedrock (on `aws-bedrock` branch)
- **Persistent memory** stored locally or in S3
- **Tool-based follow-up capture**: when a visitor shares an email or clearly asks to stay in touch, the agent uses tools to trigger a Mailjet-backed notification so potential recruiters/clients can easily follow up.
- **Unanswered-question logging**: whenever the agent cannot confidently answer a question from the provided context, it uses a tool to log that question so it can be reviewed and addressed later.
- **Response judge & guardrails**: a separate evaluator model reviews the latest answer to detect prompt hijacking, hallucinations, off-topic or unprofessional replies, and can trigger a rerun with feedback to keep the twin on-brand and safe.
- **Production-ready infra** with Terraform, API keys via API Gateway usage plans
- **Clean UI** built with Next.js and Tailwind-style classes

> Note: In production, API keys are enforced at API Gateway. Locally, the backend does not require API keys.

---

## Architecture Overview
- **Frontend** (`frontend/`)
  - Next.js 16, React 19
  - Static export (`frontend/next.config.ts` sets `output: 'export'`)
  - Main chat component: `frontend/components/twin.tsx` (calls backend `/chat`)
- **Backend** (`backend/`)
  - FastAPI app in `backend/server.py`
  - Lambda wrapper via `backend/lambda_handler.py` (Mangum)
  - Prompt and profile context in `backend/context.py`
  - Deployment packaging script: `backend/deploy.py`
- **Infrastructure** (`terraform/`)
  - API Gateway, Lambda, S3 (frontend + memory), CloudFront
  - Outputs: `api_gateway_url`, `cloudfront_url`, etc. (`terraform/outputs.tf`)
- **Scripts** (`scripts/`)
  - Deploy infra + frontend: `scripts/deploy.sh`
  - Destroy infra: `scripts/destroy.sh`

---

## Branches & AI Providers
- **`main` (default)** — uses OpenRouter
  - Config in `backend/server.py` via `OpenAI(base_url=https://openrouter.ai/api/v1)`
  - Model example: `google/gemini-2.5-flash-lite`
- **`aws-bedrock`** — uses Amazon Bedrock
  - Reads `BEDROCK_MODEL_ID` and uses `bedrock-runtime` client
  - Useful for AWS-native deployments where Bedrock access is available

Switch branches depending on your provider. Both share the same API contract for the frontend (`/chat`, `/health`, `/conversation/{session_id}`).

---

## API Endpoints (Backend)
- `GET /health` — basic health check
- `POST /chat` — body: `{ message: string, session_id?: string }` → returns `{ response, session_id }`
- `GET /conversation/{session_id}` — retrieve persisted messages

The backend maintains conversation history and limits context to recent messages. See `backend/server.py` for details.

---

## Prerequisites
- Python 3.12
- Node.js 18+ and npm
- Docker (for building the Lambda package)
- AWS CLI v2 and Terraform (for infra deployment)
- uv (for deployment script) — install via:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  ```

---

## Quick Start (Local Development)

### 1) Clone
```bash
git clone <this-repo>
cd ai-twin
```

### 2) Backend (FastAPI)
```bash
# create a virtual env (optional)
python -m venv .venv && source .venv/bin/activate

# install deps
pip install -r backend/requirements.txt

# set local env (edit .env or export here)
# minimal for local OpenRouter mode
export OPENROUTER_API_KEY=sk-or-...
export CORS_ORIGINS=http://localhost:3000

# run locally
uvicorn backend.server:app --reload --port 8000
```

### 3) Frontend (Next.js)
```bash
cd frontend
npm install

# Create .env.local with local settings
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
# Leave stage empty for local FastAPI (no API Gateway stage)
NEXT_PUBLIC_BASE_STAGE_NAME=
# Not required locally, only used by API Gateway in prod
NEXT_PUBLIC_CHAT_ENDPOINT_API_KEY=local-dev
EOF

# run frontend dev server (default: http://localhost:3000)
npm run dev
```
> If you prefer using port 3001, either run `npm run dev -- -p 3001` or update `CORS_ORIGINS` in `.env` accordingly.

Open http://localhost:3000 and start chatting.

---

## Environment Variables

### Root `.env` (read by backend and scripts)
- `OPENROUTER_API_KEY` — required on `main` branch for OpenRouter
- `DEFAULT_MODEL_NAME` — default chat model slug (e.g., `google/gemini-2.5-flash-lite`)
- `EVALUATION_MODEL_NAME` — evaluator model slug (defaults to `DEFAULT_MODEL_NAME` when unset)
- `EVALUATION_PROVIDER_ORDER_ENABLED` — `true|false` toggle (defaults to `false`) to apply the provider order; fallbacks stay enabled
- `EVALUATION_PROVIDER_ORDER` — comma-separated provider slugs in priority order for the evaluator
- `CORS_ORIGINS` — comma-separated origins for CORS (e.g., `http://localhost:3000`)
- `DEFAULT_AWS_REGION` — e.g., `ap-south-1`
- `PROJECT_NAME` — used in infra naming
- `BEDROCK_MODEL_ID` — e.g., `apac.amazon.nova-lite-v1:0` (used on `aws-bedrock` branch)
- `USE_S3` — `true|false` to store conversation memory in S3
- `S3_BUCKET` — bucket for memory when `USE_S3=true`
- `MEMORY_DIR` — local memory folder when `USE_S3=false` (default: `../memory` relative to backend)
- Optional for CI/deploy scripts: `AWS_ACCOUNT_ID`

### Frontend env
- `NEXT_PUBLIC_API_URL` — base URL of API Gateway (prod) or FastAPI (local)
- `NEXT_PUBLIC_BASE_STAGE_NAME` — API Gateway stage name (e.g., `prod`), leave empty locally
- `NEXT_PUBLIC_CHAT_ENDPOINT_API_KEY` — required in prod, enforced by API Gateway
- `NEXT_PUBLIC_HEALTH_ENDPOINT_API_KEY` — optional, if you protect health in API GW
- `NEXT_PUBLIC_BASE_ENDPOINT_API_KEY` — optional

Example production env (generated by deploy script): `frontend/.env.production`.

---

## Deployment (AWS)

### Option 1: Manual Deployment
Prerequisites:
- AWS CLI configured with appropriate credentials
- Terraform installed
- Docker available (for Lambda package build)

```bash
# from repo root
./scripts/deploy.sh <environment> <project_name>
# examples
./scripts/deploy.sh dev twin
./scripts/deploy.sh prod twin
```
What it does:
- Builds Lambda package via Docker (`backend/deploy.py`)
- Runs `terraform init/apply` in `terraform/`
- Builds the Next.js site and uploads to the frontend S3 bucket
- Prints CloudFront and API Gateway URLs

The script reads `.env` and passes `OPENROUTER_API_KEY` to Terraform as `TF_VAR_openrouter_api_key`.

> The deploy script invokes `uv run backend/deploy.py`. Ensure `uv` is installed and on PATH (see Prerequisites).

### Option 2: GitHub Actions (CI/CD)
The project includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) for automated deployments:

**Triggering a Deployment:**
1. **Manual Trigger**: Go to Actions → Workflows → Deploy Digital Twin → Run workflow
   - Select environment (`dev` or `prod`)
   - Click "Run workflow"

2. **Push to Branches**:
   - Pushing to `main` triggers a `dev` environment deployment
   - Pushing a git tag (e.g., `v1.0.0`) triggers a `prod` environment deployment

**Required GitHub Secrets:**
- `AWS_ROLE_ARN`: IAM Role ARN with deployment permissions
- `AWS_ACCOUNT_ID`: Your AWS account ID
- `DEFAULT_AWS_REGION`: AWS region (e.g., `us-east-1`)
- `OPENROUTER_API_KEY`: Your OpenRouter API key (for main branch)
- `BEDROCK_MODEL_ID`: (Optional) For aws-bedrock branch deployments

**Workflow Steps:**
1. Checks out code
2. Sets up AWS credentials using OIDC
3. Installs dependencies (Python, Node.js, Terraform)
4. Runs deployment script
5. Invalidates CloudFront cache
6. Posts deployment summary with URLs

**Note**: The workflow automatically configures CORS and sets up the required infrastructure using Terraform on the first run.

### 2) Destroy
```bash
./scripts/destroy.sh <environment> [project_name]
```
Cleans S3 buckets, and runs `terraform destroy` for the workspace.

---

## Tech Stack

| Category         | Technologies |
|------------------|--------------|
| **Frontend**     | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons |
| **Backend**      | FastAPI, Uvicorn, Mangum (Lambda), Pydantic, Python 3.12 |
| **AI**           | OpenRouter (main) / Amazon Bedrock (aws-bedrock branch) |
| **Infrastructure** | AWS Lambda, API Gateway, S3, CloudFront, Route 53, CloudWatch |
| **DevOps**       | Terraform, GitHub Actions, Docker |
| **Testing**      | Pytest, Jest, React Testing Library |
| **Security**     | IAM, API Keys, GitHub Secrets, VPC |

**Key Features**:
- **Frontend**: Modern React with TypeScript and responsive design
- **Backend**: Serverless FastAPI with Lambda support
- **AI**: Dual-provider support (OpenRouter & Bedrock)
- **Infrastructure**: Fully automated IaC with Terraform
- **CI/CD**: GitHub Actions for automated testing and deployment

---

## Development Workflow

### Local Development
1. **Start the backend**:
   ```bash
   # In project root
   cd backend
   # Set up environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   
   # Run FastAPI server
   uvicorn server:app --reload --port 8000
   ```

2. **Start the frontend**:
   ```bash
   # In a new terminal
   cd frontend
   npm install
   npm run dev
   ```
   Access the app at `http://localhost:3000`

### Testing Changes
- **Backend tests**:
  ```bash
  cd backend
  python -m pytest tests/
  ```
- **Frontend tests**:
  ```bash
  cd frontend
  npm test
  ```

## Security Best Practices

### Authentication & Authorization
- **OIDC Authentication**: GitHub Actions uses OIDC to authenticate with AWS, eliminating the need for long-lived credentials
- **Least Privilege IAM**: IAM roles are scoped to only necessary permissions for each component
- **API Gateway API Keys**: Required for production endpoints to prevent unauthorized access
- **Environment Variables**: Sensitive values are stored in GitHub Secrets and injected at runtime

### Secure Development
- **Dependencies**: Regularly update dependencies to patch security vulnerabilities
- **Secrets Management**: Never commit secrets to version control
- **Infrastructure as Code**: All resources are defined in Terraform for auditability
- **CORS**: Strict CORS policies are enforced in production

## Troubleshooting

### Common Issues
- **CORS errors**: 
  - Ensure `CORS_ORIGINS` includes your frontend URL (e.g., `http://localhost:3000`)
  - Check API Gateway CORS settings if using custom domains

- **Local dev 404 at `/dev/chat`**: 
  - Set `NEXT_PUBLIC_BASE_STAGE_NAME` to empty string in local development
  - Verify backend is running on the expected port (default: 8000)

- **API key errors (prod)**: 
  - Ensure API keys are configured in API Gateway
  - Verify `NEXT_PUBLIC_CHAT_ENDPOINT_API_KEY` is set in frontend environment
  - Check API Gateway usage plans and API key associations

- **Lambda packaging issues**: 
  - Verify Docker is running
  - Check available disk space (minimum 2GB free space required)
  - The deploy script uses `public.ecr.aws/lambda/python:3.12` image

- **Model access**: 
  - **OpenRouter**: Verify `OPENROUTER_API_KEY` is valid and has sufficient credits
  - **Bedrock**: Confirm `BEDROCK_MODEL_ID` is correct and IAM roles have `bedrock:InvokeModel` permission

- **Terraform state issues**:
  ```bash
  # If you encounter state lock errors
  terraform force-unlock LOCK_ID
  
  # To refresh state
  terraform refresh
  ```

### Debugging
- **Frontend**: Check browser developer console for errors
- **Backend**: Check CloudWatch logs for Lambda functions
- **API Gateway**: Enable CloudWatch logs for detailed request/response logging
- **Terraform**: Use `TF_LOG=DEBUG` for verbose output during deployment

---

## Security & Privacy

### Data Protection
- **No Data Storage**: The application does not store personal data permanently
- **Temporary Memory**: Conversation history is stored in-memory or in a dedicated S3 bucket

### Compliance
- **GDPR/CCPA Ready**: No personal data is stored long-term
- **Infrastructure Security**:
  - **IMPORTANT**: This project does not include DDoS protection by default.
  - **Strongly Recommended**: Enable AWS WAF and Shield Advanced to protect against DDoS attacks.
  - **Financial Responsibility**: Without proper DDoS protection, your AWS account may be vulnerable to high traffic attacks that could result in significant AWS charges. The project maintainers are not responsible for any costs incurred due to DDoS attacks or unauthorized usage of your AWS resources.
  - **Security Best Practices**:
    - Set up AWS Budgets and billing alerts
    - Configure AWS WAF rules to block suspicious traffic
    - Consider using AWS Shield Advanced for enhanced DDoS protection
    - Regularly monitor your AWS billing dashboard

### Best Practices
1. **Secrets Management**:
   - Store all secrets in GitHub Secrets
   - Never commit `.env` files or hardcoded credentials
   - Rotate API keys and credentials regularly

2. **Infrastructure Security**:
   - Use IAM roles with least privilege
   - Enable AWS CloudTrail for audit logging
   - Regular security scanning of dependencies
   - Infrastructure changes through PRs with required approvals

3. **Application Security**:
   - Input validation on all API endpoints
   - CORS policies restricted to known origins
   - Security headers (CSP, XSS Protection, etc.)
   - Regular dependency updates to patch vulnerabilities

---

## License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
