# Baseera AI: OSINT Due Diligence Agent

Baseera is an enterprise-grade, multi-agent AI system designed to automate strategic due diligence and market research. Built for high-stakes consulting workflows, it translates ambiguous research goals into custom, MECE-compliant issue trees and executes parallel Open-Source Intelligence (OSINT) gathering.

## The Generative AI Engine

Baseera goes beyond standard Retrieval-Augmented Generation (RAG) by applying generative reasoning at every stage of the pipeline:

* **Generative Planning:** The `planner_node` uses an LLM to generate a custom consulting framework and targeted search queries based on the client's core objective.
* **Generative Extraction:** The `researcher_node` reads unstructured HTML from live web searches and synthesizes it into clean, structured Pydantic data objects.
* **Generative Reasoning (Fact-Checking):** An independent `domain_fact_checker_node` logically evaluates extracted claims against source evidence, classifying them as Verified, Unverified, or Contradicted to prevent hallucinations.
* **Generative Synthesis & Reporting:** Verified facts are synthesized into a cohesive strategic executive summary, culminating in an auto-generated, quantitatively enriched Markdown report.

## System Architecture

Baseera utilizes a graph-based state machine to route data between specialized LLM agents, featuring a Human-in-the-Loop (HITL) pause for steering before final synthesis.

    ```mermaid
    graph TD
        Start((Start))
        Planner[planner_node<br/><i>Generates MECE Issue Tree</i>]
        Review[plan_review_node<br/><i>Human-in-the-Loop Approval</i>]
        
        subgraph Parallel OSINT Domains
            Wrapper[domain_wrapper_node]
            Extractor[research_extraction<br/><i>Generates Structured Claims</i>]
            Verifier[fact_checking<br/><i>LLM Verifies Evidence</i>]
            
            Wrapper --> Extractor
            Extractor --> Verifier
        end

        Synthesizer[synthesizer_node<br/><i>Cross-Domain Analysis</i>]
        Writer[report_writer_node<br/><i>Generates Final Markdown Report</i>]
        End((End))

        Start --> Planner
        Planner --> Review
        Review -- "route_to_subgraphs" --> Wrapper
        Verifier --> Synthesizer
        Synthesizer --> Writer
        Writer --> End

        classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
        classDef special fill:#e1d5e7,stroke:#9673a6,stroke-width:2px;
        class Planner,Extractor,Verifier,Synthesizer,Writer special;
    ```


## Tech Stack
* **AI Orchestration & Logic:** LangGraph, LangChain, OpenAI (GPT-4o-mini), Pydantic
* **OSINT Tools:** Tavily Search API, YouTube Transcript API
* **Backend & API:** Python, FastAPI, WebSockets
* **Frontend & Visualization:** Streamlit, Markdown, WeasyPrint (PDF Generation)
* **DevOps:** Docker, Docker Compose

## Repository Structure

    ```text
    ├── src/baseera/          
    │   ├── graph.py          
    │   ├── nodes.py          
    │   ├── state.py          
    │   └── tools.py          
    ├── app.py                
    ├── main.py               
    ├── Dockerfile            
    ├── docker-compose.yml    
    └── requirements.txt      
    ```

## Local Quickstart

1. **Clone the repository:**
    ```bash
    git clone [https://github.com/Rana-Alnajashi/baseera-ai.git](https://github.com/Rana-Alnajashi/baseera-ai.git)
    cd baseera-ai
    ```
2. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your API credentials:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    TAVILY_API_KEY=your_tavily_api_key
    ```
3. **Build and Launch via Docker:**
    ```bash
    docker-compose up --build
    ```
4. **Access the Application:**
   Open your browser and navigate to `http://localhost:8501`.