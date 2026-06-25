---
inclusion: always
---

# Technology Stack

<!--
  INSTRUCTIONS: Document your chosen stack so Kiro prefers your established tools over alternatives.
  Be specific about versions where they constrain choices (e.g. Node 18 LTS, not "Node").
  Aim for <80 lines. Remove sections that don't apply to your project.
-->

## Languages

- **[Language 1]** [version] — [where used: e.g. "primary backend language"]
- **[Language 2]** [version] — [where used: e.g. "infrastructure as code (Terraform)"]

## Frontend

<!-- Remove this section entirely if the project has no frontend -->
- **Framework:** [e.g. React 18 / Next.js 14 / Vue 3 / None]
- **Styling:** [e.g. Tailwind CSS 3 / CSS Modules / styled-components]
- **State management:** [e.g. Zustand / Redux Toolkit / React Query / Context only]
- **Build tool:** [e.g. Vite / Next.js built-in / Webpack 5]
- **Package manager:** [e.g. pnpm / npm / yarn] — [always use this, not alternatives]
- **Testing:** [e.g. Vitest + React Testing Library / Jest + Enzyme]

## Backend

<!-- Remove this section entirely if the project has no backend -->
- **Framework:** [e.g. Express 4 / Fastify 4 / Django 4.2 / FastAPI 0.100]
- **Runtime:** [e.g. Node.js 20 LTS / Python 3.11 / JVM 21]
- **ORM / query layer:** [e.g. Prisma / SQLAlchemy / TypeORM / raw SQL via pg]
- **API style:** [e.g. REST / GraphQL (Apollo Server) / gRPC / tRPC]
- **Auth:** [e.g. Passport.js with OIDC / FastAPI OAuth2 / Spring Security]
- **Testing:** [e.g. Jest + Supertest / pytest + httpx / JUnit 5 + MockMvc]

## Database & Storage

- **Primary database:** [e.g. PostgreSQL 15 / MySQL 8 / MongoDB 7]
- **Cache:** [e.g. Redis 7 / None]
- **Object storage:** [e.g. AWS S3 / None]
- **Migrations:** [e.g. Flyway / Alembic / Prisma Migrate]

## Infrastructure & Deployment

- **Cloud provider:** [e.g. AWS / GCP / Azure / Multi-cloud / On-prem]
- **Container runtime:** [e.g. Docker / Podman / None]
- **Orchestration:** [e.g. Kubernetes (EKS) / ECS Fargate / Cloud Run / None]
- **IaC:** [e.g. Terraform / CDK / Pulumi / None]
- **CI/CD:** [e.g. GitHub Actions / GitLab CI / Jenkins]
- **Secrets management:** [e.g. AWS Secrets Manager / HashiCorp Vault / Azure Key Vault]
- **Observability:** [e.g. Datadog / AWS CloudWatch / Grafana + Prometheus / OpenTelemetry]

## Developer Tooling

- **Linter:** [e.g. ESLint with @typescript-eslint / Ruff / Pylint]
- **Formatter:** [e.g. Prettier / Black / gofmt]
- **Type checking:** [e.g. TypeScript strict mode / mypy / None]
- **Pre-commit hooks:** [e.g. Husky + lint-staged / pre-commit / None]

## Approved & Prohibited Libraries

<!-- This is the highest-value section — Kiro will default to these instead of alternatives -->

### Always Use (Approved)
- **HTTP client:** [e.g. axios / fetch (built-in) / httpx] — do not add alternatives
- **Date handling:** [e.g. date-fns / dayjs / Arrow]
- **Validation:** [e.g. Zod / Joi / Pydantic v2]
- **Logging:** [e.g. pino / Winston / structlog / Loguru]

### Never Use (Prohibited)
- [e.g. "moment.js — banned, use date-fns instead"]
- [e.g. "eval() and Function() constructor — security policy"]
- [e.g. "console.log in production code — use the structured logger"]

## Technical Constraints

- [e.g. "All new packages require security review via the JIRA SEC-REVIEW process"]
- [e.g. "No external network calls in unit tests — mock all HTTP"]
