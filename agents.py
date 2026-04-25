import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"  # Change to: mistral, gemma2, phi3, etc.


def call_ollama(prompt: str, system_prompt: str = "") -> str:
    """Call local Ollama model and return response text."""
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        response.raise_for_status()
        return response.json().get("response", "No response received.")
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to Ollama. Run `ollama serve` and ensure the model is pulled."
    except requests.exceptions.Timeout:
        return "❌ Request timed out. Try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"


def outline_designer(topic, goals, funding_agency, org_type, duration, extra_context, memory):
    """Agent 1: Designs a full grant proposal outline."""
    system_prompt = """You are an expert grant writer with 20+ years of experience 
    helping researchers and nonprofits win competitive grants from major funding agencies.
    You write clear, compelling, agency-aligned proposal outlines.
    Use proper grant writing structure and terminology."""

    # Include prior context from memory if available
    prior_context = ""
    if memory.get("latest_review"):
        prior_context = f"\n\nPrevious reviewer feedback to incorporate:\n{memory['latest_review'][:500]}"

    prompt = f"""Design a comprehensive grant proposal outline for the following:

Topic: {topic}
Project Goals: {goals}
Funding Agency: {funding_agency}
Organization Type: {org_type}
Project Duration: {duration}
Additional Context: {extra_context or 'None'}
{prior_context}

Please create a detailed outline with these sections:
1. **Executive Summary / Abstract** (150 words max guidance)
2. **Problem Statement / Need** — Why this matters, evidence of need
3. **Goals and Objectives** — SMART objectives tied to the goals
4. **Methodology / Project Design** — How you will achieve objectives
5. **Evaluation Plan** — How success will be measured
6. **Organizational Capacity** — Why your org is qualified
7. **Sustainability Plan** — How the project continues after funding
8. **Timeline** — Milestones for {duration}
9. **Key Personnel** — Roles needed

For each section, include:
- Purpose of the section
- 3-5 bullet points of key content to include
- Writing tips specific to {funding_agency}

End with a 'Competitive Differentiators' section — what makes this proposal stand out."""

    return call_ollama(prompt, system_prompt)


def budget_estimator(topic, goals, funding_agency, org_type, duration, budget_range,
                     team_size, indirect_rate, budget_notes, memory):
    """Agent 2: Estimates a detailed grant budget."""
    system_prompt = """You are a grants financial specialist who creates detailed, 
    compliant, and justified grant budgets for research and nonprofit proposals.
    You know the budget requirements of major funding agencies and follow OMB Uniform Guidance.
    Always justify each line item and flag common compliance issues."""

    prompt = f"""Create a detailed grant budget estimate for:

Topic: {topic}
Funding Agency: {funding_agency}
Organization Type: {org_type}
Project Duration: {duration}
Budget Range: {budget_range}
Team Size: {team_size} people
Indirect Cost Rate: {indirect_rate}%
Budget Notes: {budget_notes or 'None'}

Provide a full budget breakdown:

**SECTION A — PERSONNEL**
List roles, effort %, and estimated annual salaries for a team of {team_size}.
Include fringe benefits (estimate 30% of salaries).

**SECTION B — EQUIPMENT**
Any equipment >$5,000 per unit needed for {topic}.

**SECTION C — TRAVEL**
Conferences, field work, site visits relevant to {topic}.

**SECTION D — SUPPLIES & MATERIALS**
Lab supplies, software, printing, etc.

**SECTION E — CONSULTANTS / SUBCONTRACTS**
Any external expertise needed.

**SECTION F — OTHER DIRECT COSTS**
Participant support, publication costs, etc.

**SECTION G — INDIRECT COSTS (F&A)**
Calculate at {indirect_rate}% of Modified Total Direct Costs (MTDC).

**BUDGET SUMMARY TABLE**
| Category | Year 1 | Year 2 (if applicable) | Total |
Show totals and verify against {budget_range}.

**BUDGET JUSTIFICATION TIPS**
5 key points to justify this budget to {funding_agency} reviewers.

**COMPLIANCE FLAGS**
Note any common budget compliance issues for {funding_agency}."""

    return call_ollama(prompt, system_prompt)


def reviewer_simulation(topic, goals, funding_agency, reviewer_type, content, memory):
    """Agent 3: Simulates expert peer review of the proposal."""
    reviewer_personas = {
        "Strict Academic Peer Reviewer": """You are a senior academic peer reviewer with expertise in the field.
        You are rigorous, skeptical, and hold proposals to the highest scientific standards.
        You look for methodological rigor, innovation, feasibility, and impact.""",

        "Program Officer (Agency Side)": """You are an experienced Program Officer at a major funding agency.
        You assess alignment with agency priorities, compliance with requirements,
        organizational capacity, and value for money. You are strategic and mission-focused.""",

        "Community Impact Evaluator": """You are a community impact evaluator who prioritizes 
        equity, real-world outcomes, community engagement, and sustainability.
        You look for evidence of community voice, inclusive practices, and measurable social impact.""",

        "Budget & Compliance Reviewer": """You are a grants compliance officer reviewing financial 
        and administrative aspects. You check for budget justification, allowable costs, 
        indirect rate accuracy, and adherence to funding agency regulations."""
    }

    system_prompt = reviewer_personas.get(reviewer_type, reviewer_personas["Strict Academic Peer Reviewer"])

    prompt = f"""Review this grant proposal for {funding_agency}:

Topic: {topic}
Goals: {goals}

PROPOSAL CONTENT:
{content}

As a {reviewer_type}, provide detailed feedback:

**OVERALL SCORE** — Rate 1-10 with brief justification

**STRENGTHS** (3-5 bullet points)
What is compelling and well-done?

**WEAKNESSES** (3-5 bullet points)
What are the significant gaps or concerns?

**CRITICAL ISSUES** (must fix before submission)
Any fatal flaws that would cause rejection?

**SECTION-BY-SECTION FEEDBACK**
Go through each section and provide specific comments.

**RECOMMENDED REVISIONS** (prioritized)
List the top 5 changes needed, in priority order.

**FUNDING LIKELIHOOD**
Your honest assessment: Likely Funded / Competitive / Needs Major Revision / Not Fundable
Explain why.

**SUGGESTED RESOURCES**
Any additional data, citations, or sections that would strengthen this proposal."""

    return call_ollama(prompt, system_prompt)
