import streamlit as st
from datetime import datetime
from agents import outline_designer, budget_estimator, reviewer_simulation
from memory import load_memory, save_memory, add_version, get_versions

st.set_page_config(page_title="Grant Proposal Assistant", page_icon="📋", layout="wide")

st.title("📋 AI-Powered Grant Proposal Assistant")
st.caption("Powered by Ollama — Helps researchers & nonprofits draft winning proposals")

# ── Sidebar: Proposal Setup ───────────────────────────────────────────────────
with st.sidebar:
    st.header("🎯 Proposal Setup")

    topic = st.text_input("Research / Project Topic", placeholder="e.g. Climate-resilient urban farming")
    goals = st.text_area("Project Goals", placeholder="e.g. Reduce food insecurity, develop low-water crops...")
    funding_agency = st.text_input("Funding Agency", placeholder="e.g. NIH, NSF, Gates Foundation, USDA")
    org_type = st.selectbox("Organization Type", ["University / Research Institute", "Nonprofit", "Government Agency", "Private Company", "Individual Researcher"])
    duration = st.selectbox("Project Duration", ["6 months", "1 year", "2 years", "3 years", "5 years"])
    budget_range = st.selectbox("Budget Range", ["Under $50,000", "$50K–$200K", "$200K–$500K", "$500K–$1M", "Over $1M"])

    st.divider()
    st.header("🧠 Memory")
    memory = load_memory(topic) if topic else {}
    versions = get_versions(topic) if topic else []
    if versions:
        st.write(f"**Saved versions:** {len(versions)}")
        for v in versions[-3:]:
            st.caption(f"v{v['version']} — {v['timestamp'][:16]}")
    else:
        st.caption("No versions saved yet.")

    if st.button("🗑️ Clear Topic Memory", use_container_width=True):
        if topic:
            save_memory(topic, {})
            st.success("Memory cleared!")
            st.rerun()

# Guard
if not topic:
    st.info("👈 Enter your project topic and details in the sidebar to begin.")
    st.stop()

# Load memory for this topic
memory = load_memory(topic)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Outline Designer",
    "💰 Budget Estimator",
    "🔍 Reviewer Simulation",
    "📜 Version History",
    "📤 Export"
])

# ── TAB 1: Outline Designer ───────────────────────────────────────────────────
with tab1:
    st.subheader("📝 Outline Designer Agent")
    st.write(f"**Topic:** {topic} | **Agency:** {funding_agency} | **Duration:** {duration}")

    # Show previous outline if exists
    if memory.get("latest_outline"):
        st.info("📌 A previous outline exists for this topic. Generate a new one to update it.")
        with st.expander("View Current Outline"):
            st.markdown(memory["latest_outline"])

    extra_context = st.text_area(
        "Additional context (optional)",
        placeholder="Any specific requirements, prior work, key researchers, institutional strengths...",
        key="outline_context"
    )

    if st.button("✨ Generate Outline", type="primary", use_container_width=True):
        if not goals or not funding_agency:
            st.warning("Please fill in Goals and Funding Agency in the sidebar.")
        else:
            with st.spinner("🤖 Outline Designer Agent is working..."):
                result = outline_designer(topic, goals, funding_agency, org_type, duration, extra_context, memory)

            st.markdown("### Generated Outline")
            st.markdown(result)

            # Save to memory and version
            memory["latest_outline"] = result
            memory["topic"] = topic
            memory["funding_agency"] = funding_agency
            memory["goals"] = goals
            memory["org_type"] = org_type
            memory["duration"] = duration
            save_memory(topic, memory)
            add_version(topic, "outline", result, rationale=f"Generated outline for {funding_agency}")
            st.success("✅ Outline saved to memory!")

# ── TAB 2: Budget Estimator ───────────────────────────────────────────────────
with tab2:
    st.subheader("💰 Budget Estimator Agent")

    team_size = st.number_input("Team Size", min_value=1, max_value=50, value=3)
    indirect_rate = st.slider("Indirect Cost Rate (%)", 0, 60, 26)
    budget_notes = st.text_area(
        "Budget Notes (optional)",
        placeholder="e.g. Need 2 postdocs, field travel to 3 sites, lab equipment..."
    )

    if st.button("💰 Estimate Budget", type="primary", use_container_width=True):
        with st.spinner("🤖 Budget Estimator Agent is calculating..."):
            result = budget_estimator(
                topic, goals, funding_agency, org_type,
                duration, budget_range, team_size, indirect_rate, budget_notes, memory
            )

        st.markdown("### Budget Breakdown")
        st.markdown(result)

        memory["latest_budget"] = result
        save_memory(topic, memory)
        add_version(topic, "budget", result, rationale=f"Budget for {budget_range}, {duration}, team of {team_size}")
        st.success("✅ Budget saved to memory!")

# ── TAB 3: Reviewer Simulation ────────────────────────────────────────────────
with tab3:
    st.subheader("🔍 Reviewer Simulation Agent")
    st.caption("Simulates expert peer review of your proposal to identify weaknesses before submission.")

    reviewer_type = st.selectbox(
        "Reviewer Perspective",
        ["Strict Academic Peer Reviewer", "Program Officer (Agency Side)", "Community Impact Evaluator", "Budget & Compliance Reviewer"]
    )

    # Pull in latest content to review
    content_to_review = ""
    if memory.get("latest_outline"):
        content_to_review += f"\n\nOUTLINE:\n{memory['latest_outline']}"
    if memory.get("latest_budget"):
        content_to_review += f"\n\nBUDGET:\n{memory['latest_budget']}"

    if not content_to_review:
        st.warning("Generate an Outline and/or Budget first so the reviewer has content to evaluate.")
    else:
        st.info(f"Will review: {'Outline ✅' if memory.get('latest_outline') else ''} {'Budget ✅' if memory.get('latest_budget') else ''}")

        if st.button("🔍 Run Reviewer Simulation", type="primary", use_container_width=True):
            with st.spinner(f"🤖 Simulating {reviewer_type}..."):
                result = reviewer_simulation(
                    topic, goals, funding_agency, reviewer_type, content_to_review, memory
                )

            st.markdown("### Reviewer Feedback")
            st.markdown(result)

            memory["latest_review"] = result
            memory["reviewer_type"] = reviewer_type
            save_memory(topic, memory)
            add_version(topic, "review", result, rationale=f"Review by {reviewer_type}")
            st.success("✅ Review saved to memory!")

# ── TAB 4: Version History ────────────────────────────────────────────────────
with tab4:
    st.subheader("📜 Version History")

    versions = get_versions(topic)
    if not versions:
        st.info("No versions saved yet. Generate content in the other tabs.")
    else:
        for v in reversed(versions):
            label = f"v{v['version']} | {v['type'].upper()} | {v['timestamp'][:16]}"
            if v.get("rationale"):
                label += f" — {v['rationale']}"
            with st.expander(label):
                st.markdown(v["content"])

        st.divider()
        st.write(f"**Total versions:** {len(versions)}")

        # Show memory context
        st.subheader("🧠 Topic Memory")
        display_mem = {k: v for k, v in memory.items() if k not in ["latest_outline", "latest_budget", "latest_review"]}
        if display_mem:
            st.json(display_mem)
        else:
            st.caption("No metadata saved yet.")

# ── TAB 5: Export ─────────────────────────────────────────────────────────────
with tab5:
    st.subheader("📤 Export Proposal")

    if not any([memory.get("latest_outline"), memory.get("latest_budget"), memory.get("latest_review")]):
        st.info("Generate content in the other tabs first, then export here.")
    else:
        include_outline = st.checkbox("Include Outline", value=bool(memory.get("latest_outline")))
        include_budget = st.checkbox("Include Budget", value=bool(memory.get("latest_budget")))
        include_review = st.checkbox("Include Reviewer Feedback", value=bool(memory.get("latest_review")))

        if st.button("📄 Build Export Document", type="primary", use_container_width=True):
            lines = [
                f"GRANT PROPOSAL DRAFT",
                f"{'=' * 50}",
                f"Topic          : {topic}",
                f"Funding Agency : {funding_agency}",
                f"Organization   : {org_type}",
                f"Duration       : {duration}",
                f"Budget Range   : {budget_range}",
                f"Generated      : {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"{'=' * 50}",
                ""
            ]

            if include_outline and memory.get("latest_outline"):
                lines += ["", "SECTION 1: PROPOSAL OUTLINE", "-" * 40, memory["latest_outline"], ""]

            if include_budget and memory.get("latest_budget"):
                lines += ["", "SECTION 2: BUDGET ESTIMATE", "-" * 40, memory["latest_budget"], ""]

            if include_review and memory.get("latest_review"):
                lines += ["", "SECTION 3: REVIEWER FEEDBACK", "-" * 40,
                          f"Reviewer Type: {memory.get('reviewer_type', 'N/A')}",
                          memory["latest_review"], ""]

            lines += [
                "",
                f"{'=' * 50}",
                f"VERSION SUMMARY",
                f"Total versions: {len(get_versions(topic))}",
            ]
            for v in get_versions(topic):
                lines.append(f"  v{v['version']} [{v['type']}] {v['timestamp'][:16]} — {v.get('rationale', '')}")

            export_text = "\n".join(lines)
            filename = f"grant_proposal_{topic[:30].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"

            st.download_button(
                "⬇️ Download Proposal (.txt)",
                data=export_text,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )
            st.text_area("Preview", export_text, height=400)
