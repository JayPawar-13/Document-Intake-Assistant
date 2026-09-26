# Production Readiness & Improvement Roadmap

This document outlines the architectural enhancements, security controls, and operational tooling required to graduate the **Document Intake Assistant** prototype into a commercial, enterprise-grade production platform.

---

## 1. Authentication & Role-Based Access Control (RBAC)

- **Authentication**:
  - Integrate OAuth 2.0 / OpenID Connect (OIDC) via providers like Auth0, Clerk, or AWS Cognito.
  - Implement passwordless magic links or multi-factor authentication (MFA/TOTP) for clients submitting sensitive estate details.
- **Authorization & Multi-Tenancy**:
  - Implement tenant isolation so law firms or financial advisory practices can manage their own clients independently.
  - Role hierarchy:
    - `Client / Testator`: Can only access and edit their assigned session.
    - `Advisor / Paralegal`: Can review client drafts, suggest annotations, and invite clients.
    - `Managing Partner / Admin`: Full firm-level access, user management, and billing.

---

## 2. Data Protection, Privacy & Encryption

- **Encryption in Transit & at Rest**:
  - Enforce TLS 1.3 for all client-to-backend and backend-to-database communications.
  - Enable MongoDB Encrypted Storage Engine (WiredTiger encryption at rest) with customer-managed keys (AWS KMS / Azure Key Vault).
  - Implement Field-Level Encryption (FLE) or Client-Side Field Level Encryption (CSFLE) for sensitive PII:
    - Full legal names
    - Street addresses
    - Children's names and relationships
- **Data Privacy & Compliance (GDPR / UK DPA 2018)**:
  - "Right to be Forgotten" endpoint that scrubs sessions, messages, and state records from MongoDB.
  - Granular consent tracking recorded upon session initialization.
  - Configurable data retention policies (e.g., auto-purge drafts inactive for 90 days).

---

## 3. Audit Logging & Compliance Trails

- **Immutable Audit Log**:
  - Implement an append-only audit trail collection capturing every state mutation:
    - Who initiated the change (User ID, IP, User Agent).
    - Previous value vs new value (JSON diff).
    - Source of change (Conversational extraction vs Manual PATCH edit).
    - Timestamp (UTC ISO 8601).
  - Hash-chain audit records to guarantee tamper-evidence for legal defensibility.

---

## 4. LLM Reliability, Observability & Failover

- **Observability & Tracing**:
  - Integrate tools like **Langfuse**, **Arize Phoenix**, or **OpenLLMetry / OpenTelemetry** to log token consumption, latency, and extraction fidelity.
  - Capture input prompts and structured JSON outputs for continual offline evaluation.
- **Model Fallback & High Availability**:
  - Implement an automated failover circuit breaker:
    - Primary: `gpt-4o` / `gpt-4o-mini` with strict JSON schema mode.
    - Secondary: Anthropic `claude-3-5-sonnet` / `claude-3-haiku` via LiteLLM.
    - Graceful fallback to deterministic rule engine if all remote LLM endpoints fail or rate limits are reached.
- **Guardrails**:
  - Integrate NeMo Guardrails or Llama Guard to detect prompt injections, jailbreaks, or attempts to extract system instructions.

---

## 5. Rate Limiting & Denial-of-Service Protection

- Implement Redis-backed sliding-window rate limiting on all conversational endpoints:
  - 30 requests/minute per authenticated user.
  - 10 requests/minute per unauthenticated IP on session creation.
- Request payload size limits (reject messages over 2,000 characters).

---

## 6. Database Scalability & High Availability

- **Replica Sets & Sharding**:
  - Transition from single-node local MongoDB to a 3-node replica set on MongoDB Atlas or Kubernetes.
  - Continuous automated snapshots with Point-in-Time Recovery (PITR).
- **Index Optimization**:
  - Optimize compound indexes on `{ "session_id": 1, "created_at": -1 }`.
  - Add TTL indexes for transient session cleanup.

---

## 7. Legal Disclaimer & Digital Execution Integration

- **Legal Validity Disclaimers**:
  - Prominent watermarking distinguishing non-binding expressions of wishes from statutory Wills (Wills Act 1837 in the UK).
  - Step-by-step guidance advising testators to review with a qualified solicitor.
- **E-Signature & Identity Verification (eIDV)**:
  - Integrate DocuSign or Adobe Sign APIs for witness attestation and qualified electronic signatures (QES).
  - Integrate Jumio / Onfido for KYC / identity verification where legally required.
