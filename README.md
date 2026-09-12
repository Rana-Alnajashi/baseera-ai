# Baseera AI: OSINT Due Diligence Agent

Baseera is a multi-agent AI system designed to automate strategic due diligence and market research. Built for enterprise consulting workflows, it translates ambiguous research goals into custom, MECE-compliant issue trees and executes parallel Open-Source Intelligence (OSINT) gathering.

## Key Features
* **Hypothesis-Driven Planning:** Utilizes LLMs to break down high-level research goals into targeted domains.
* **Agentic OSINT Workflows:** Employs LangGraph to orchestrate parallel web search (Tavily) and YouTube transcript extraction.
* **Rigorous Fact-Checking:** Features a dedicated verification node to evaluate extracted claims against source evidence, rejecting hallucinations and unsupported PR language.
* **Human-in-the-Loop (HITL):** Suspends execution via WebSockets to allow human analyst review before committing to web research and during final synthesis steering.
* **Automated Report Generation:** Synthesizes cross-domain insights into a professional Markdown and PDF report.

## Tech Stack
* **Orchestration:** LangGraph, LangChain, OpenAI (GPT-4o-mini)
* **Backend:** FastAPI, WebSockets
* **Frontend:** Streamlit
* **Infrastructure:** Docker, Docker Compose

## Local Quickstart
1. Clone the repository: 
   `git clone https://github.com/Rana-Alnajashi/baseera-ai.git`
2. Create a `.env` file in the root directory and add your credentials:
   `OPENAI_API_KEY=your_key_here`
   `TAVILY_API_KEY=your_key_here`
3. Build and launch the multi-container environment: 
   `docker-compose up --build`
4. Access the Streamlit UI at `http://localhost:8501`. 