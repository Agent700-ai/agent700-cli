# A700cli Product Overview

**For Product Owners & Stakeholders**  
**Version:** 2.0  
**Last Updated:** 2026-01-29

---

## Executive Summary

A700cli is a command-line interface for Agent700 that enables users to interact with AI agents from the terminal. It supports both interactive conversations and automated workflows, making it suitable for developers, operations teams, and automation pipelines.

---

## Product Capabilities

### 1. Chat & Conversation

**What it does:** Send messages to AI agents and receive intelligent responses.

| Mode | Best For | Example |
|------|----------|---------|
| Interactive | Ongoing conversations | `a700cli --interactive` |
| Single message | Quick queries | `a700cli "What is the weather?"` |
| Streaming | Real-time responses | `a700cli "Explain this" --streaming` |

**Sample: Interactive Chat Session**
```
$ a700cli --interactive

Interactive Agent700 Chat
Commands: /exit, /quit, /q, /clear, /context, /help

You: What can you help me with today?

Agent: I can help you with:
- Code review and analysis
- Data processing and insights
- Documentation generation
- Research and information lookup
- And much more! What would you like to do?

You: /exit
Goodbye!
```

**Sample: Single Message**
```
$ a700cli "Summarize the key features of Python 3.12"

Agent: Python 3.12 introduces several key features:
1. Improved error messages with more precise locations
2. Per-interpreter GIL for better multi-threading
3. Type parameter syntax for generic classes
4. F-string improvements with arbitrary expressions
...
```

---

### 2. Agent Management

**What it does:** Discover, create, update, and manage AI agents.

**Agent selection without upfront config**

You don't have to define an agent in `.env` before running. When `AGENT_UUID` is missing, the CLI prompts you to enter an agent UUID. Use `--list-agents` (and `--search`) to discover agents; then run chat or interactive and enter the UUID when prompted. To use a different agent later, run the CLI again and enter a different UUID when prompted; the chosen agent is saved to `.env` for the next run.

| Action | Command | Purpose |
|--------|---------|---------|
| List agents | `--list-agents` | Find available agents |
| Search agents | `--list-agents --search "code"` | Filter by name |
| Show details | `--show-agent <ID>` | View agent configuration |
| Create agent | `--create-agent` | Create new agent |
| Update agent | `--update-agent <ID>` | Modify agent settings |
| Delete agent | `--delete-agent <ID>` | Remove agent |

**Sample: Discovering Agents**
```
$ a700cli --list-agents --search "review"

Available Agents (Page 1 of 1)
┌────────────────────┬──────────────┐
│ NAME               │ UUID         │
├────────────────────┼──────────────┤
│ Code Reviewer      │ a1b2c3d4...  │
│ PR Review Bot      │ e5f6g7h8...  │
│ Security Reviewer  │ i9j0k1l2...  │
└────────────────────┴──────────────┘

Choose an agent when you run the CLI (e.g. run chat or interactive and enter the UUID when prompted).
```

**Sample: Creating an Agent**
```
$ a700cli --create-agent \
    --agent-org "org-123" \
    --agent-name "Customer Support Bot" \
    --agent-model "gpt-4o" \
    --agent-prompt "You are a helpful customer support agent..."

Agent created. ID: new-agent-uuid-here
```

---

### 3. Organization Management

**What it does:** View and manage organization memberships.

**Sample: List Organizations**
```
$ a700cli --list-orgs

Organizations
┌──────────────────────────────────────┬────────────────┬─────────┐
│ ID                                   │ NAME           │ ROLE    │
├──────────────────────────────────────┼────────────────┼─────────┤
│ org-abc-123                          │ Acme Corp      │ admin   │
│ org-def-456                          │ Dev Team       │ member  │
└──────────────────────────────────────┴────────────────┴─────────┘
```

---

### 4. MCP Tool Integration

**What it does:** Agents can use external tools (search, databases, APIs) via the Model Context Protocol (MCP).

| Command | Purpose |
|---------|---------|
| `--list-mcp-servers` | Show available MCP servers |
| `--mcp-tools <ID>` | List tools for an agent |
| `--mcp-health <ID>` | Check MCP server health |

**Sample: List MCP Tools**
```
$ a700cli --mcp-tools a1b2c3d4-e5f6-7890-abcd-ef1234567890

MCP tools for agent a1b2c3d4...:
  • brave-search: Search the web using Brave Search API
  • fetch: Fetch content from a URL
  • memory: Store and retrieve information
```

**Sample: Agent Using Tools**
```
$ a700cli "What's the latest news about AI?" --streaming

Agent: Let me search for the latest AI news...

[Tool: brave-search] Searching: "latest AI news 2026"

Based on recent search results:
1. OpenAI announced GPT-5 with improved reasoning...
2. Google DeepMind released Gemini Ultra 2...
3. Anthropic published new safety research...
```

---

### 5. File Input/Output

**What it does:** Read prompts from files and save responses to files.

| Option | Purpose | Example |
|--------|---------|---------|
| `--input-file` | Read prompt from file | `a700cli -f prompt.txt` |
| `--output-file` | Save response to file | `a700cli "..." -o result.txt` |
| stdin | Pipe input | `cat data.txt \| a700cli` |

**Sample: Processing a Document**
```
$ cat contract.txt | a700cli "Summarize this contract" -o summary.txt

Wrote response to summary.txt

$ cat summary.txt
This contract establishes a 2-year service agreement between...
Key terms:
- Monthly fee: $5,000
- Termination: 30 days notice
- Liability cap: $100,000
```

**Sample: Batch Processing**
```bash
#!/bin/bash
for file in reports/*.txt; do
    a700cli "Analyze this report" -f "$file" -o "analysis/$(basename $file)"
done
```

---

### 6. Automation & Scripting

**What it does:** Integrate with CI/CD pipelines, scripts, and automation workflows.

| Feature | Purpose |
|---------|---------|
| `--quiet` | Minimal output (stdout only) |
| Exit codes | 0 = success, 1 = error |
| JSON output | `--format json` for structured data |

**Sample: CI/CD Integration**
```bash
#!/bin/bash
# Generate deployment report in CI pipeline

response=$(a700cli "Generate deployment report for $BRANCH" --quiet)

if [ $? -eq 0 ]; then
    echo "Deployment Report:"
    echo "$response"
else
    echo "Failed to generate report"
    exit 1
fi
```

**Sample: Quiet Mode for Scripting**
```
$ result=$(a700cli "What is 2+2?" --quiet)
$ echo "Answer: $result"
Answer: 4
```

---

### 7. App Passwords

**What it does:** Create secure tokens for API access without using your main password.

| Command | Purpose |
|---------|---------|
| `--create-app-password NAME` | Create new app password |
| `--list-app-passwords` | List existing passwords |
| `--delete-app-password ID` | Revoke a password |

**Sample: Create App Password**
```
$ a700cli --create-app-password "CI Pipeline Token"

App password created. Store the token securely; it will not be shown again.
Token: ap_1234567890abcdef...
```

---

### 8. Billing & Usage

**What it does:** View usage metrics and costs.

**Sample: View Usage**
```
$ a700cli --billing-usage --start-date 2026-01-01 --end-date 2026-01-29

Total cost: $45.23

Billing Logs
┌─────────────┬───────────────┬───────────────────┬─────────┐
│ Model       │ Prompt Tokens │ Completion Tokens │ Cost    │
├─────────────┼───────────────┼───────────────────┼─────────┤
│ gpt-4o      │ 125,000       │ 45,000            │ $32.50  │
│ gpt-4o-mini │ 250,000       │ 100,000           │ $12.73  │
└─────────────┴───────────────┴───────────────────┴─────────┘
```

---

### 9. QA & Ratings

**What it does:** Submit quality ratings and export rating data.

| Command | Purpose |
|---------|---------|
| `--rate` | Submit a rating (with --agent-id, --revision-id, --score) |
| `--export-ratings` | Export ratings as CSV |

**Sample: Submit Rating**
```
$ a700cli --rate \
    --agent-id "a1b2c3d4" \
    --revision-id 5 \
    --score 4 \
    --rating-notes "Good response quality, minor formatting issues"

Rating submitted.
```

---

### 10. Context Library

**What it does:** Store and retrieve key-value data that agents can reference.

| Command | Purpose |
|---------|---------|
| `--context-library-list` | List all entries |
| `--context-library-get KEY` | Get value by key |
| `--context-library-set KEY VALUE` | Set a value |
| `--context-library-delete KEY` | Delete an entry |

**Sample: Managing Context**
```
$ a700cli --context-library-set "company_name" "Acme Corporation"
Context library entry set.

$ a700cli --context-library-get "company_name"
Acme Corporation

$ a700cli --context-library-list
Context library:
  company_name: Acme Corporation
  support_email: help@acme.com
  timezone: America/New_York
```

---

### 11. Document Parsing

**What it does:** Extract text from documents (PDF, DOCX, etc.).

**Sample: Parse Document**
```
$ a700cli --parse-document report.pdf

[Extracted text from report.pdf]

QUARTERLY FINANCIAL REPORT
Q4 2025

Executive Summary
This quarter saw significant growth across all business units...
```

---

## Feature Matrix by Use Case

| Use Case | Features Used | Sample Command |
|----------|--------------|----------------|
| **Developer Chat** | Interactive, streaming | `a700cli -i --streaming` |
| **Code Review** | Single message, file I/O | `a700cli "Review this" -f code.py` |
| **CI/CD Automation** | Quiet mode, exit codes | `a700cli "Deploy check" -q` |
| **Batch Processing** | File I/O, scripting | `a700cli -f input.txt -o output.txt` |
| **Admin Tasks** | Agent/org management | `a700cli --list-agents` |
| **Cost Monitoring** | Billing commands | `a700cli --billing-usage` |
| **Quality Tracking** | Ratings export | `a700cli --export-ratings -o ratings.csv` |

---

## Industry Use Cases

### Healthcare

**Features used:** File I/O (`-f`, `-o`), `--parse-document`, stdin piping. Use `--quiet` in scripts to avoid logging PHI.

**Use case: Patient data summarization**

Summarize clinical notes or discharge summaries for care coordination.

```
$ a700cli "Summarize this discharge summary. List medications, follow-up instructions, and red flags." -f discharge_notes.txt -o summary.txt

$ cat summary.txt
Summary:
- Medications: Metformin 500mg BID, Lisinopril 10mg daily...
- Follow-up: Cardiology in 2 weeks, PCP in 1 month
- Red flags: Monitor blood sugar; report chest pain
```

**Use case: Medical record analysis**

Parse and analyze uploaded documents (e.g., lab results, referrals) without exposing raw PHI in prompts.

```
$ a700cli --parse-document lab_results.pdf | a700cli "Extract key findings and flag abnormal values" -o findings.txt

$ head findings.txt
Key findings:
- HbA1c: 7.2% (elevated; target <7%)
- LDL: 98 mg/dL (within range)
- Flag: Creatinine elevated; suggest nephrology follow-up
```

**Use case: Clinical note generation**

Generate structured notes from a brief prompt for documentation support.

```
$ a700cli "Generate a SOAP note for: 65yo male, HTN and DM2, here for 3-month follow-up. BP 128/82, A1c 7.1. Continue current meds, add statin. RTC 3 months." -o soap_note.txt
```

**Use case: HIPAA-compliant document processing**

Process documents via file I/O and parse-document so raw PHI stays in files; only summaries or extracted fields go to the agent. Use app passwords and quiet mode in automation to limit exposure.

```
$ a700cli --parse-document referral.pdf | a700cli "Extract referring MD, reason for referral, and urgency only" -o referral_summary.txt -q
```

---

### Finance & Banking

**Features used:** File I/O, `--format json` for structured data, `--quiet` in pipelines. Use `--list-orgs` and app passwords for CI.

**Use case: Transaction analysis**

Analyze transaction exports or statements for anomalies or categorization.

```
$ a700cli "Categorize these transactions and flag any unusual or high-risk patterns." -f transactions_jan.csv -o categorized.csv
```

**Use case: Risk assessment reports**

Generate narrative risk summaries from structured data.

```
$ a700cli "Write a one-page credit risk summary for this portfolio. Include concentration, sector, and liquidity risks." -f portfolio_data.json -o risk_summary.txt
```

**Use case: Regulatory compliance checks**

Review policy or procedure text for alignment with a regulation.

```
$ a700cli "Check this AML policy against typical FinCEN guidance. List gaps and suggested additions." -f aml_policy.docx -o compliance_gaps.txt
```

**Use case: Financial document parsing**

Extract text from statements, reports, or PDFs, then analyze or summarize.

```
$ a700cli --parse-document quarterly_statement.pdf | a700cli "List total assets, liabilities, and net change vs prior quarter" -o summary.txt
```

---

### Legal

**Features used:** File I/O, `--parse-document`, batch loops, MCP search (`--streaming`) for research.

**Use case: Contract review and summarization**

Summarize contracts and highlight key terms and obligations.

```
$ a700cli "Summarize this NDA. List: parties, term, confidentiality scope, exclusions, and termination." -f nda.pdf -o nda_summary.txt

$ cat nda_summary.txt
Parties: Acme Corp (Disclosing), Beta Inc (Receiving)
Term: 3 years from execution
Confidentiality: All non-public business and technical information
Exclusions: Public domain, independently developed, rightfully received
Termination: 30 days written notice; survival 2 years
```

**Use case: Due diligence document analysis**

Batch-analyze documents for relevance and key points.

```
$ for f in diligence_docs/*.pdf; do
    a700cli --parse-document "$f" | a700cli "List material commitments and obligations" -o "analysis/$(basename "$f" .pdf).txt"
  done
```

**Use case: Case research**

Use MCP search tools to gather recent case law or regulatory updates.

```
$ a700cli "What are the latest court rulings on non-compete enforceability in California in 2025?" --streaming
```

**Use case: Compliance audit support**

Batch-review policies or procedures against a checklist and produce gap reports.

```
$ a700cli "Against a standard data-retention audit checklist, list which items are covered in this policy and which are missing." -f policy.pdf -o audit_gaps.txt
```

---

### E-commerce & Retail

**Features used:** File I/O, `-o` for generated copy, CSV/Excel input. Use `--format json` for catalog feeds.

**Use case: Product description generation**

Generate consistent, SEO-friendly product copy from attributes.

```
$ a700cli "Write a 150-word product description for: wireless earbuds, 24hr battery, noise canceling, $79.99. Tone: professional, feature-focused." -o product_desc.txt
```

**Use case: Customer review analysis**

Summarize feedback and extract themes from review text.

```
$ a700cli "Summarize these reviews. List top 3 positives, top 3 complaints, and one sentence overall sentiment." -f reviews_export.csv -o review_summary.txt
```

**Use case: Inventory and pricing analysis**

Interpret inventory or pricing exports and suggest actions.

```
$ a700cli "From this inventory report, identify slow-moving SKUs and suggest a markdown strategy." -f inventory_report.xlsx -o markdown_suggestions.txt
```

**Use case: Inventory report generation**

Generate narrative or structured reports from inventory data.

```
$ a700cli "Turn this inventory export into a one-page executive summary: top movers, stockouts, and reorder suggestions." -f inventory_export.csv -o inventory_report.txt
```

---

### Manufacturing & Logistics

**Features used:** File I/O, `--parse-document` for PDFs, batch scripts. Use `--quiet` in cron or CI.

**Use case: Quality control report analysis**

Summarize QC results and flag out-of-spec or trending issues.

```
$ a700cli "Summarize this QC report. List batches out of spec, any trends, and recommended actions." -f qc_report_jan.pdf -o qc_summary.txt
```

**Use case: Supply chain documentation**

Turn shipment or PO data into short narrative updates.

```
$ a700cli "Turn this shipment log into a one-paragraph status update for management: on-time, delays, and open issues." -f shipment_log.csv -o status_update.txt
```

**Use case: Maintenance log processing**

Extract patterns and recommendations from maintenance records.

```
$ a700cli "From these maintenance logs, list recurring issues, suggested PM intervals, and parts to stock." -f maintenance_logs.txt -o maintenance_insights.txt
```

**Use case: Shipping document generation**

Generate BOL, packing lists, or status updates from shipment data.

```
$ a700cli "Generate a short shipping status summary: on-time deliveries, delays, and exceptions. Use neutral tone." -f shipment_data.csv -o shipping_summary.txt
```

---

### Education

**Features used:** File I/O, CSV for evaluations, `-o` for outlines and summaries. Use `--format json` for LMS integration.

**Use case: Course content generation**

Generate outlines, readings, or assignment prompts.

```
$ a700cli "Create a 5-topic outline for a 1-day workshop on Python for data science, with one exercise per topic." -o workshop_outline.txt
```

**Use case: Student feedback analysis**

Summarize course evaluations and extract actionable themes.

```
$ a700cli "Summarize these course evaluations. List strengths, improvements requested, and one overall recommendation." -f evals_fall.csv -o eval_summary.txt
```

**Use case: Research paper summarization**

Summarize papers or extract key claims and methodology.

```
$ a700cli "Summarize this paper: research question, method, main findings, and limitations." -f paper.pdf -o paper_summary.txt
```

**Use case: Assignment grading assistance**

Generate rubrics, sample feedback, or consistency checks from assignment prompts and submissions (instructor use only).

```
$ a700cli "Given this assignment prompt and rubric, produce 2 sample feedback paragraphs: one for a strong submission and one for a weak submission." -f assignment_prompt.txt -o sample_feedback.txt
```

---

## Authentication Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    First-Time Setup                          │
├──────────────────────────────────────────────────────────────┤
│  1. Run: a700cli --interactive                               │
│  2. Enter email and password when prompted                   │
│  3. Enter agent UUID (use --list-agents to find)             │
│  4. Configuration saved to .env file                         │
│  5. Future runs use saved credentials automatically          │
└──────────────────────────────────────────────────────────────┘
```

---

## Output Formats

| Format | Best For | How to Get |
|--------|----------|------------|
| Rich (default) | Human reading | Default output |
| JSON | Automation, APIs | `--format json` |
| Plain text | Simple scripts | `--quiet` |

---

## Roadmap Features

### Planned: Client-Side Tool Execution (In Development)

Currently, MCP tools are executed server-side. The upcoming client-side tool execution feature will:

- Detect tool calls in streamed responses
- Execute tools locally (faster, more control)
- Support both local MCP servers (subprocess) and remote MCP servers (API)
- Enable agentic loops that continue until task completion

See [`docs/specs/2026-01-29-tool-execution.md`](specs/2026-01-29-tool-execution.md) for technical details.

---

## Support

- **Email:** hello@agent700.ai
- **Docs:** https://agent700.ai/docs
- **Help:** `a700cli --help`
