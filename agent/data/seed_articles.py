"""
Seed script — creates 10 JSON batch files in agent/data/queue/.
Each file contains 3 articles covering the 8 canonical categories.

Usage:
    python agent/data/seed_articles.py          # from repo root
    python data/seed_articles.py                # from inside the agent container

The agent picks up files from queue/, classifies each article, publishes
to BullMQ and moves the file to processed/.
"""

import json
from pathlib import Path

QUEUE_DIR = Path(__file__).parent / "queue"

# 30 articles spread across 10 batch files (3 per file).
# Each article is crafted to hit clear keyword signals so the classifier
# assigns the correct category without needing the AI fallback.
BATCHES = [
    # Batch 1 — technology, ai, business
    [
        {
            "title": "TypeScript 6.0 Delivers 60% Faster Compilation for Large Codebases",
            "source": "InfoQ",
            "content": (
                "The TypeScript team shipped version 6.0 today, featuring a rewritten "
                "compiler backend that reduces build times by up to 60 percent on "
                "monorepos with more than 500,000 lines of code. "
                "The new architecture uses incremental type resolution and smarter caching "
                "of module graphs, meaning that developers working on large software projects "
                "can iterate far faster between saves. "
                "Microsoft benchmarked the improvement across 12 open-source TypeScript "
                "codebases and found median build time dropped from 38 seconds to under 16 seconds."
            ),
            "published_at": "2026-06-18T07:00:00Z",
        },
        {
            "title": "OpenAI GPT-5 Sets Record on Every Major LLM Benchmark",
            "source": "MIT Technology Review",
            "content": (
                "OpenAI released GPT-5 today, and independent evaluators at Stanford's "
                "Center for AI Safety report the model achieves top scores on all seven "
                "major large language model evaluation suites simultaneously — a first "
                "in the history of AI research. "
                "The neural architecture introduces sparse attention that allows the model "
                "to process 2 million tokens of context without the quadratic cost typical "
                "of transformer-based LLMs. "
                "OpenAI confirmed pricing will start at $15 per million input tokens for the "
                "full model and $1.50 for the distilled variant, which runs at comparable "
                "speeds to GPT-4."
            ),
            "published_at": "2026-06-18T07:30:00Z",
        },
        {
            "title": "Sequoia Capital Closes $10B Fund Targeting AI Infrastructure Startups",
            "source": "Bloomberg",
            "content": (
                "Sequoia Capital has closed its largest-ever fund at $10.3 billion, with a "
                "stated focus on early and growth-stage startup companies building foundational "
                "infrastructure for artificial intelligence workloads, sources familiar with "
                "the matter confirmed today. "
                "The fund received investment commitments from sovereign wealth funds in "
                "Abu Dhabi, Singapore, and Norway, alongside university endowments collectively "
                "managing over $800 billion. "
                "Sequoia partners described their thesis as a bet on picks-and-shovels — "
                "companies supplying compute orchestration, vector databases, and observability "
                "tooling that all AI product teams require, regardless of which LLM ultimately "
                "wins the model race."
            ),
            "published_at": "2026-06-18T08:00:00Z",
        },
    ],
    # Batch 2 — science, health, politics
    [
        {
            "title": "Researchers Confirm Room-Temperature Superconductor at Moderate Pressure",
            "source": "Physical Review Letters",
            "content": (
                "Scientists at the Max Planck Institute published findings today confirming "
                "that a hydrogen-enriched lutetium compound exhibits zero electrical resistance "
                "at 22 degrees Celsius under pressures 150 times atmospheric — a 40-fold "
                "reduction from previous room-temperature superconductor candidates. "
                "Independent researchers at MIT and RIKEN in Japan replicated the core results "
                "using separate sample batches, lending significant credibility to a field that "
                "has historically suffered from reproducibility problems. "
                "If the pressure requirement can be further reduced, the discovery would enable "
                "lossless transmission grids and quantum computers that operate without "
                "cryogenic cooling."
            ),
            "published_at": "2026-06-18T08:30:00Z",
        },
        {
            "title": "mRNA Vaccine Shows 94% Efficacy Against Pancreatic Cancer in Phase III Trial",
            "source": "The Lancet",
            "content": (
                "A personalized mRNA vaccine co-developed by Moderna and Memorial Sloan "
                "Kettering achieved 94 percent efficacy in preventing disease recurrence "
                "among surgically treated pancreatic cancer patients in a 1,157-person "
                "Phase III clinical trial published today. "
                "Each vaccine is manufactured individually from DNA sequencing of the "
                "patient's tumor, training the immune system to destroy cells carrying "
                "that specific mutation profile — a treatment approach that differs "
                "fundamentally from conventional cancer medicine. "
                "The FDA granted the therapy Priority Review designation and is expected "
                "to issue an approval decision within six months, which would make it "
                "the first personalized cancer vaccine approved for any solid tumor."
            ),
            "published_at": "2026-06-18T09:00:00Z",
        },
        {
            "title": "European Parliament Passes AI Liability Directive in 387-145 Vote",
            "source": "Reuters",
            "content": (
                "The European Parliament voted 387 to 145 today to adopt the AI Liability "
                "Directive, establishing a legally binding framework that holds AI system "
                "developers accountable for harms caused by their products across all "
                "27 EU member states. "
                "The legislation requires companies deploying high-risk AI in healthcare, "
                "finance, and critical infrastructure to maintain audit logs for ten years "
                "and respond to transparency requests within 30 working days. "
                "Penalties scale from 1 percent of global annual revenue for procedural "
                "violations up to 6 percent for substantive breaches, with the most serious "
                "cases referred to national criminal prosecution authorities."
            ),
            "published_at": "2026-06-18T09:30:00Z",
        },
    ],
    # Batch 3 — sports, general, technology
    [
        {
            "title": "Brazil Wins Copa America 2026 in Penalty Shootout Over Argentina",
            "source": "ESPN",
            "content": (
                "Brazil claimed the Copa America 2026 championship in a penalty shootout "
                "at the Rose Bowl in Los Angeles, ending a six-year title drought and "
                "reigniting the sport's most celebrated international rivalry on its "
                "grandest stage. "
                "The championship match ended 1-1 after 120 minutes, with Vinicius Jr. "
                "scoring Brazil's opener in the 34th minute before Messi equalized from "
                "a free kick with 11 minutes left in regulation. "
                "Brazilian goalkeeper Ederson saved two penalties in the shootout, which "
                "Brazil converted 4-2, and the stadium gave Messi — expected to retire "
                "from international football — a standing ovation as he left the pitch."
            ),
            "published_at": "2026-06-18T10:00:00Z",
        },
        {
            "title": "Universal Basic Income Pilot in Finland Shows 8% Rise in Employment",
            "source": "The Guardian",
            "content": (
                "A five-year universal basic income pilot conducted across 15 Finnish "
                "municipalities recorded an 8 percent increase in formal employment among "
                "recipients compared with a matched control group, according to the final "
                "government report published today. "
                "Participants receiving €750 per month unconditionally reported significantly "
                "higher wellbeing scores and were more likely to start a business or pursue "
                "vocational retraining than those in the welfare comparison group. "
                "The Finnish government said it will use the findings to redesign the national "
                "social security system, though a full UBI rollout has not been announced."
            ),
            "published_at": "2026-06-18T10:30:00Z",
        },
        {
            "title": "Apple M4 Ultra Chip Doubles Neural Engine Performance for On-Device AI",
            "source": "The Verge",
            "content": (
                "Apple introduced the M4 Ultra processor at its annual developer conference "
                "today, integrating 200 billion transistors on a single die and doubling "
                "the neural engine throughput compared with the M3 generation. "
                "The chip executes 800 trillion AI operations per second, allowing developers "
                "to run large language model inference entirely on hardware without routing "
                "requests to cloud servers. "
                "The M4 Ultra will ship inside updated Mac Pro and Mac Studio hardware "
                "starting next month, with Apple citing significant improvements in "
                "Final Cut Pro render times and Xcode compilation speed."
            ),
            "published_at": "2026-06-18T11:00:00Z",
        },
    ],
    # Batch 4 — ai, science, health
    [
        {
            "title": "DeepMind AlphaFold 3 Predicts Protein-Ligand Binding with 95% Accuracy",
            "source": "Nature",
            "content": (
                "Google DeepMind published AlphaFold 3 today, a major upgrade to its "
                "protein structure prediction platform that now models interactions between "
                "proteins and small-molecule drug candidates with 95 percent accuracy — "
                "a capability previous deep learning models could not reliably achieve. "
                "The system was trained on 200 million protein-ligand complexes from the "
                "Protein Data Bank and uses a diffusion-based architecture that can predict "
                "binding poses without expensive wet-lab experiments. "
                "Pharmaceutical companies including Pfizer and Novartis have already "
                "integrated AlphaFold 3 into their early drug-discovery pipelines, "
                "reporting that time to identify viable clinical candidates dropped "
                "from three years to under eight months."
            ),
            "published_at": "2026-06-18T11:30:00Z",
        },
        {
            "title": "CRISPR Gene Editing Eliminates Sickle Cell Disease in 15-Year Study",
            "source": "New England Journal of Medicine",
            "content": (
                "A 15-year clinical study published today confirms that CRISPR-Cas9 gene "
                "editing permanently eliminated sickle cell disease symptoms in 97 percent "
                "of patients who received the treatment as children, tracking 210 participants "
                "across 12 hospitals in the US and UK. "
                "Scientists found that edited stem cells continued producing functional "
                "hemoglobin throughout the entire observation period without any sign of "
                "diminishing efficacy, marking the first curative treatment for a major "
                "inherited blood disorder proven safe over a decade-plus timeframe. "
                "Regulatory agencies in both countries are expected to expand approval of "
                "the therapy to adult patients following the landmark findings."
            ),
            "published_at": "2026-06-18T12:00:00Z",
        },
        {
            "title": "AI Radiology Tool Reduces Diagnostic Errors by 60% in 47-Hospital Study",
            "source": "JAMA",
            "content": (
                "A study of 3.4 million radiological scans across 47 US hospital networks "
                "published in JAMA today found that AI-assisted image interpretation reduced "
                "clinically significant diagnostic errors by 60 percent compared with "
                "radiologist-only review conducted under standard conditions. "
                "Researchers noted that the AI system maintained consistent accuracy "
                "throughout 12-hour shifts while human-only error rates climbed by an "
                "average of 23 percent in the final four hours — a pattern consistent "
                "with cognitive fatigue. "
                "Patients receiving AI-assisted diagnoses began treatment an average of "
                "4.2 days sooner than those in the standard-care group, a difference "
                "that translates into meaningfully better outcomes for fast-progressing "
                "conditions like sepsis and stroke."
            ),
            "published_at": "2026-06-18T12:30:00Z",
        },
    ],
    # Batch 5 — business, politics, science
    [
        {
            "title": "Amazon Expands Same-Day Delivery to 50 Latin American Cities",
            "source": "Reuters",
            "content": (
                "Amazon announced today the expansion of its same-day delivery service "
                "to 50 cities across Brazil, Mexico, Colombia, and Argentina, partnering "
                "with more than 300 local logistics startups to build the last-mile "
                "fulfillment network at a stated investment of $2 billion over three years. "
                "Early data from São Paulo and Mexico City pilots shows same-day delivery "
                "achieving a 98.3 percent on-time rate, exceeding the company's "
                "North American performance baseline. "
                "The expansion positions Amazon to compete directly with Mercado Libre, "
                "which has spent five years building its own proprietary logistics arm "
                "across the region."
            ),
            "published_at": "2026-06-18T13:00:00Z",
        },
        {
            "title": "US Senate Passes Comprehensive AI Regulation Bill 67-31",
            "source": "Politico",
            "content": (
                "The US Senate passed the Algorithmic Accountability and Safety Act today "
                "in a 67-31 bipartisan vote, establishing the first federal legal framework "
                "governing the development and deployment of artificial intelligence systems "
                "in the United States. "
                "The legislation requires annual third-party audits for AI systems used "
                "in consequential decisions involving credit, employment, housing, and "
                "medical treatment, with fines of up to $50 million per violation for "
                "companies that fail to comply. "
                "The bill now moves to the House, where leadership has signaled it will "
                "schedule a floor vote within 30 days."
            ),
            "published_at": "2026-06-18T13:30:00Z",
        },
        {
            "title": "MIT Engineers Create Self-Healing Concrete Using Dormant Bacteria",
            "source": "MIT News",
            "content": (
                "Civil engineers at MIT published results today showing that a concrete "
                "formulation containing dormant bacterial spores can autonomously seal "
                "structural cracks up to 0.8 millimeters wide within 28 days of damage, "
                "without any human intervention. "
                "Laboratory tests across 200 samples subjected to freeze-thaw cycling "
                "showed self-healed specimens recovered 94 percent of original compressive "
                "strength — outperforming epoxy injection repairs, which typically restore "
                "70 to 80 percent. "
                "Three commercial concrete manufacturers have signed licensing agreements "
                "with MIT and plan to offer the product for bridge deck and tunnel "
                "lining applications beginning next year."
            ),
            "published_at": "2026-06-18T14:00:00Z",
        },
    ],
    # Batch 6 — technology, sports, general
    [
        {
            "title": "Rust Programming Language Overtakes C++ in Systems Development Survey",
            "source": "Stack Overflow",
            "content": (
                "The annual State of Developer Ecosystem survey published today shows "
                "Rust has overtaken C++ in adoption for new systems programming projects "
                "for the first time, with 34 percent of respondents citing Rust as their "
                "primary systems language versus 29 percent for C++. "
                "Major factors cited include Rust's memory safety guarantees enforced at "
                "compile time, zero-cost abstractions, and a crate ecosystem that now "
                "lists more than 150,000 packages. "
                "AWS, Google Cloud, and Cloudflare all published engineering blog posts "
                "this year detailing migrations of core infrastructure components "
                "from C++ to Rust, citing reduced production incidents from memory bugs."
            ),
            "published_at": "2026-06-18T14:30:00Z",
        },
        {
            "title": "Formula 1 Introduces Budget Cap Enforcement as Teams Face Record Fines",
            "source": "BBC Sport",
            "content": (
                "Formula 1's governing body announced today that three constructor teams "
                "exceeded the $135 million cost cap in the 2025 season and face fines "
                "totalling $47 million — the largest financial penalties ever issued "
                "in the sport's history. "
                "The FIA's Cost Cap Administration unit reviewed 18 months of financial "
                "submissions and found that the violations involved improper capitalization "
                "of driver simulator costs, an area the regulations clarified last season. "
                "Teams have 30 days to appeal before the fines are confirmed, and a "
                "points deduction for the 2026 championship remains possible "
                "under the adjudication panel's discretion."
            ),
            "published_at": "2026-06-18T15:00:00Z",
        },
        {
            "title": "Netflix Surpasses 350 Million Subscribers After Ad-Supported Tier Surge",
            "source": "Financial Times",
            "content": (
                "Netflix reported today that its global subscriber base crossed 350 million "
                "accounts for the first time, driven primarily by the ad-supported Standard "
                "plan which added 18 million new subscribers in the first half of 2026. "
                "The streaming platform said advertising revenue now represents 22 percent "
                "of total revenue, up from 8 percent in the same period last year, "
                "as the company deepens its investment in programmatic ad technology "
                "and live sports broadcasting rights. "
                "CEO Greg Peters cited the password-sharing crackdown and the "
                "rollout of interactive features as key drivers of subscriber retention "
                "in a market where Disney+, Max, and Apple TV+ continue to compete aggressively."
            ),
            "published_at": "2026-06-18T15:30:00Z",
        },
    ],
    # Batch 7 — health, ai, business
    [
        {
            "title": "WHO Declares End of COVID-19 Public Health Emergency of International Concern",
            "source": "WHO",
            "content": (
                "The World Health Organization formally declared today that COVID-19 no "
                "longer constitutes a Public Health Emergency of International Concern, "
                "a designation the agency first issued in January 2020, marking a "
                "symbolic milestone in the global response to the pandemic. "
                "WHO Director-General Tedros Adhanom Ghebreyesus said the decision "
                "reflects the dramatic decline in hospitalizations and deaths following "
                "widespread vaccination and natural immunity, though he cautioned that "
                "ongoing surveillance and vaccine updates remain essential. "
                "The change in emergency status does not affect national health regulations, "
                "and individual governments retain authority over travel, testing, "
                "and treatment protocols."
            ),
            "published_at": "2026-06-18T16:00:00Z",
        },
        {
            "title": "Anthropic Claude 4 Scores Top Marks on Legal and Medical Reasoning Benchmarks",
            "source": "Ars Technica",
            "content": (
                "Anthropic released Claude 4 today, and independent evaluations by "
                "Stanford's Center for AI Safety show the model achieves 91st-percentile "
                "scores on the US Bar Exam and 89th percentile on the United States Medical "
                "Licensing Examination — the strongest results recorded for any publicly "
                "available large language model on these benchmarks. "
                "The new model uses a constitutional AI training approach that penalizes "
                "hallucination more aggressively than previous generations, achieving a "
                "factual accuracy rate of 96.1 percent on TruthfulQA in third-party testing. "
                "Anthropic is releasing Claude 4 through its API with tiered pricing "
                "and has confirmed the model will power the default Claude.ai experience "
                "for all subscription tiers immediately."
            ),
            "published_at": "2026-06-18T16:30:00Z",
        },
        {
            "title": "BlackRock Bitcoin ETF Surpasses $50 Billion in Assets Under Management",
            "source": "Wall Street Journal",
            "content": (
                "BlackRock's iShares Bitcoin Trust ETF crossed $50 billion in assets under "
                "management today, just nine months after its January 2025 launch, making "
                "it the fastest exchange-traded fund in history to reach that milestone "
                "by a margin of nearly two years. "
                "The fund has attracted sustained institutional inflows averaging $1.2 billion "
                "per week, driven primarily by registered investment advisors allocating "
                "Bitcoin exposure through a regulated vehicle rather than direct custody. "
                "The S&P 500's correlation with Bitcoin ETF inflows has risen to 0.62 "
                "over the past six months, suggesting institutional investors are treating "
                "the asset as a legitimate portfolio allocation rather than a speculative position."
            ),
            "published_at": "2026-06-18T17:00:00Z",
        },
    ],
    # Batch 8 — science, politics, sports
    [
        {
            "title": "SpaceX Starship Completes First Fully Successful Orbital Flight and Landing",
            "source": "Space.com",
            "content": (
                "SpaceX's Starship vehicle completed its first fully nominal orbital mission "
                "today, reaching 250 kilometers altitude before a successful deorbit burn "
                "and propulsive ocean landing in the Indian Ocean — validating the "
                "heat shield, reentry guidance, and terminal descent algorithms "
                "simultaneously in a single flight for the first time. "
                "All 33 Raptor engines on the Super Heavy booster fired nominally throughout "
                "the ascent, eliminating the engine-out failures that contributed to partial "
                "failures in the previous four test flights. "
                "NASA confirmed the result significantly de-risks the Starship Human Landing "
                "System schedule for the Artemis lunar surface mission currently targeting 2028."
            ),
            "published_at": "2026-06-18T17:30:00Z",
        },
        {
            "title": "UK Snap Election Called After Prime Minister Loses Confidence Vote",
            "source": "BBC News",
            "content": (
                "The UK Prime Minister announced a snap general election today following "
                "a confidence vote in the House of Commons that the government lost by "
                "a margin of 14 seats — the first government to fall on a confidence "
                "vote in 45 years. "
                "The vote was triggered by a rebellion within the ruling party over "
                "proposed pension reform legislation that backbench MPs said would "
                "disproportionately affect public sector workers. "
                "The election is scheduled for 40 days from today, and current polling "
                "shows the opposition Labour Party leading by 9 percentage points "
                "among likely voters in marginal constituencies."
            ),
            "published_at": "2026-06-18T18:00:00Z",
        },
        {
            "title": "Wimbledon Introduces AI Line Calling Across All Courts Starting This Year",
            "source": "The Times",
            "content": (
                "Wimbledon announced today that electronic AI line calling will replace "
                "human line judges on all 18 courts starting with this year's tournament, "
                "making the All England Club the last Grand Slam to complete the transition "
                "to fully automated officiating. "
                "The system uses an array of high-speed cameras and computer vision "
                "algorithms to track ball trajectory and determine in/out calls with "
                "sub-millimetre precision, issuing decisions in under 3 milliseconds. "
                "Players will retain the right to challenge calls through the chair umpire, "
                "but the traditional Hawkeye review system will be retired as it is now "
                "considered less accurate than the new live system."
            ),
            "published_at": "2026-06-18T18:30:00Z",
        },
    ],
    # Batch 9 — technology, health, business
    [
        {
            "title": "Google Releases Gemini 3 Ultra with Multimodal Reasoning Across Text, Image and Code",
            "source": "The Verge",
            "content": (
                "Google DeepMind released Gemini 3 Ultra today, a multimodal model that "
                "processes text, images, audio, and code within a single unified architecture "
                "rather than routing requests through separate specialized models as its "
                "predecessor did. "
                "The model achieves state-of-the-art scores on 28 of 32 standard AI "
                "evaluation benchmarks, with particularly strong results on multi-step "
                "mathematical reasoning and long-document comprehension tasks that require "
                "tracking information across more than 100 pages of context. "
                "Google is integrating Gemini 3 Ultra into Search, Workspace, and Android "
                "immediately, with the full API accessible to developers through "
                "Google Cloud at launch."
            ),
            "published_at": "2026-06-18T19:00:00Z",
        },
        {
            "title": "Alzheimer's Drug Shows 45% Cognitive Decline Reduction in 18-Month Trial",
            "source": "Nature Medicine",
            "content": (
                "Eli Lilly's experimental Alzheimer's therapy donanemab reduced the rate "
                "of cognitive decline by 45 percent compared with placebo over an 18-month "
                "Phase III trial enrolling 2,800 patients with early symptomatic disease, "
                "according to results published in Nature Medicine today. "
                "The drug works by clearing amyloid plaques from brain tissue using "
                "targeted antibodies, and the trial found that patients who cleared "
                "plaques completely showed an additional 15 percentage point reduction "
                "in decline on top of the average treatment effect. "
                "The FDA is expected to issue a final approval decision within 90 days "
                "under the agency's Accelerated Approval pathway."
            ),
            "published_at": "2026-06-18T19:30:00Z",
        },
        {
            "title": "Stripe Raises $5B Series J at $120B Valuation Ahead of Expected IPO",
            "source": "TechCrunch",
            "content": (
                "Payments infrastructure company Stripe has raised $5 billion in a Series J "
                "funding round that values the startup at $120 billion, according to "
                "a company announcement today, making it the most valuable private "
                "technology company in the United States. "
                "The round was led by sovereign wealth funds from the UAE and Singapore, "
                "with participation from Sequoia Capital and Thrive Capital, and the "
                "company said it will use the capital to accelerate expansion into "
                "the Brazilian and Indian markets. "
                "Stripe co-founder Patrick Collison confirmed the company plans to "
                "pursue an IPO within the next 18 months, subject to market conditions."
            ),
            "published_at": "2026-06-18T20:00:00Z",
        },
    ],
    # Batch 10 — science, general, ai
    [
        {
            "title": "Solar Panel Efficiency Record Broken with 47.6% Conversion Rate in Lab",
            "source": "Science",
            "content": (
                "Researchers at the National Renewable Energy Laboratory set a new world "
                "record for solar cell efficiency today, achieving 47.6 percent energy "
                "conversion under concentrated solar illumination using a six-junction "
                "concentrator cell — surpassing the previous record by 3.1 percentage points. "
                "The breakthrough used stacked semiconductor layers each tuned to absorb "
                "a specific range of the solar spectrum that conventional silicon panels "
                "would otherwise waste, and the team says the design principles could push "
                "commercial silicon panel efficiency from 24 percent to 32-35 percent by 2030. "
                "Several solar module manufacturers have already requested sample cells "
                "for integration testing."
            ),
            "published_at": "2026-06-18T20:30:00Z",
        },
        {
            "title": "Paris Opens Largest Urban Farm in Europe on Former Industrial Rooftops",
            "source": "Le Monde",
            "content": (
                "Paris inaugurated the Jardin Aérien du Grand Paris today, a 14-hectare "
                "urban farm spread across 22 interconnected rooftops in the 13th arrondissement, "
                "claiming the title of the largest rooftop growing operation in Europe. "
                "The farm produces 1,200 tonnes of fruit and vegetables annually using "
                "aeroponic and hydroponic growing systems that require 90 percent less "
                "water than conventional field agriculture. "
                "Produce from the farm is sold directly to 40 local restaurants and "
                "a weekly market, with surplus donated to food banks serving "
                "low-income households in surrounding neighborhoods."
            ),
            "published_at": "2026-06-18T21:00:00Z",
        },
        {
            "title": "Meta Releases Open-Source LLM Matching GPT-4 Performance at Half the Cost",
            "source": "Wired",
            "content": (
                "Meta AI today released Llama 4, an open-source large language model that "
                "achieves performance comparable to GPT-4 on standard benchmarks while "
                "requiring roughly half the compute to run inference, according to "
                "evaluations conducted by independent AI research group Epoch AI. "
                "The model uses a mixture-of-experts architecture with 400 billion total "
                "parameters but only 70 billion active per forward pass, making it "
                "practical to deploy on a single 8-GPU server rather than the multi-node "
                "clusters required by equivalent dense models. "
                "Meta is releasing Llama 4 under a permissive commercial license that "
                "allows businesses with fewer than 700 million monthly active users "
                "to deploy the model without paying royalties."
            ),
            "published_at": "2026-06-18T21:30:00Z",
        },
    ],
]


def main() -> None:
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    created = 0

    for i, batch in enumerate(BATCHES, start=1):
        filename = f"seed_batch_{i:02d}.json"
        path = QUEUE_DIR / filename

        if path.exists():
            print(f"  [skip] {filename} already exists")
            continue

        path.write_text(
            json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        categories = set()
        for article in batch:
            # Derive expected category from keyword hints in title/content for display
            text = (article["title"] + " " + article["content"]).lower()
            for cat in [
                "technology",
                "ai",
                "business",
                "science",
                "health",
                "politics",
                "sports",
                "general",
            ]:
                if cat in text or any(
                    kw in text
                    for kw in {
                        "technology": [
                            "software",
                            "hardware",
                            "chip",
                            "developer",
                            "compiler",
                        ],
                        "ai": [
                            "llm",
                            "gpt",
                            "neural",
                            "model",
                            "deep learning",
                            "machine learning",
                        ],
                        "business": [
                            "startup",
                            "billion",
                            "investment",
                            "revenue",
                            "valuation",
                        ],
                        "science": [
                            "researchers",
                            "laboratory",
                            "quantum",
                            "clinical",
                            "study",
                        ],
                        "health": [
                            "vaccine",
                            "cancer",
                            "hospital",
                            "medical",
                            "disease",
                        ],
                        "politics": [
                            "parliament",
                            "senate",
                            "election",
                            "government",
                            "legislation",
                        ],
                        "sports": [
                            "championship",
                            "tournament",
                            "match",
                            "goal",
                            "olympic",
                        ],
                        "general": ["netflix", "streaming", "community", "housing"],
                    }.get(cat, [])
                ):
                    categories.add(cat)
                    break
        print(f"  [created] {filename}  ({len(batch)} articles)")
        created += 1

    print(f"\nDone — {created} batch file(s) written to {QUEUE_DIR}")
    if created == 0:
        print(
            "All files already exist. Delete them from queue/ or processed/ to reseed."
        )


if __name__ == "__main__":
    main()
