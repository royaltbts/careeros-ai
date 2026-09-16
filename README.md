# CareerOS

CareerOS is a candidate-intelligence and job-application operating system designed to help a Customer Success professional identify high-value opportunities, evaluate evidence-backed fit, tailor applications, and preserve human control over external actions.

## Current Architecture

```text
Candidate Truth Profile
        ↓
Evidence Library
        ↓
Market Scout
        ↓
Job Intelligence
        ↓
Company Intelligence
        ↓
Opportunity Scoring
        ↓
Opportunity Decision
        ↓
Supervisor Case
        ↓
Supervisor Deliberation
        ↓
Supervisor Decision
        ↓
Deliberation Record
        ↓
Application Effort
        ↓
Application Strategy
        ↓
Application Package
        ↓
Human Approval
        ↓
External Authorization
```

## Core Safety Principles

- Verified facts may be used directly.
- Transferable connections require human review.
- Missing experience must never be fabricated.
- Unverified claims must never be inserted into an application.
- External applications and outreach require explicit human authorization.

## Multi-Agent Supervision

Current specialist roles include Candidate Fit, Company Intelligence, Opportunity Decision, and Risk.

The Supervisor identifies disagreements, classifies risks, and produces an explicit resolution.

Example:

```text
Candidate Fit Agent        → APPLY
Company Intelligence      → APPLY
Opportunity Decision      → APPLY
Risk Agent                → REVIEW

Supervisor                → APPLY
```

A non-blocking disagreement does not automatically stop a strong opportunity, but human review remains mandatory.

## Auditability

Supervisor decisions are persisted independently from opportunity decisions.

Deliberation records preserve agent findings, disagreements, Supervisor resolution, confidence, unresolved questions, human-review state, external-action state, and deliberation cycle ID.

## Human Review

The Review Console exposes opportunity intelligence, evidence-backed requirements, agent findings, disagreements, Supervisor resolution, safety restrictions, approval status, and external authorization state.

The system does not automatically submit applications or send outreach.

## Technology

- Python
- Pydantic
- OpenAI Agents SDK
- pytest
- JSON persistence
- Structured agent findings
- Deterministic orchestration

## Testing

Current regression status: **76 passed**.

## Project Status

The foundation is implemented.

The next engineering phase is to evolve selected deterministic specialist roles into cooperating LLM agents while preserving candidate truth, evidence governance, Supervisor deliberation, human approval, and explicit external-action authorization.

## Repository Structure

```text
app/
  agent_nodes/
  models/
  company_research_*.py
  decision_explanation.py
  deliberation_store.py
  risk_agent.py
  supervisor.py
  supervisor_case.py
  supervisor_decision_store.py
  careeros.py
  review_console.py

data/
  candidate/
  evidence/

tests/
```

## Reproducibility

Top-level dependencies are defined in `requirements.txt`.

The current development environment is captured in `requirements.lock.txt`.

`.env`, `.venv`, caches, and generated job artifacts are excluded from Git.
