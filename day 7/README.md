# 10 Days of Voice Agents — #VoiceForBharat Edition

Welcome to **10 Days of Voice Agents, #VoiceForBharat Edition**, by [murf.ai](https://murf.ai/api)!

## About the Challenge

We built **[Murf Falcon](https://murf.ai/falcon)**, the consistently fastest TTS API — and **[Falcon 2](https://murf.ai/api/docs/text-to-speech-models/falcon-2)**, our latest streaming model, gets you to ~100 ms latency. This August, you're going to use it to build voice agents for the people who need them most.

**Build one voice agent over ten days**, from August 6th to August 15th, ending on Independence Day. The agent gets a new capability every day, until it can answer a real phone call and solve a real problem for someone in India.

## Progress

| Day | Feature | Tag |
|-----|---------|-----|
| 1 | Voice agent setup + Indian voice | v0.1.0-day1 |
| 2 | Persona, guardrails, multilingual voice flow | v0.1.1-day2 |
| 3 | Frontend personalisation + agent state indicators | v2.1.0-day3 |
| 4 | Persistent user memory + database (SQLite) | v2.2.0-day4 |
| 5 | Database querying + dynamic voice responses | v2.3.0-day5 |

**Day 1 – Voice Agent Foundation:**
Started the project by setting up the LiveKit-based voice agent and integrating Murf Falcon for Indian voice output. I configured the required development environment, connected the voice pipeline, and established the initial Ratan Kirana local-commerce use case. The main goal was to get a working end-to-end voice interaction where the agent could hear the user and respond naturally, establishing the foundation for the remaining days of the challenge. This corresponds to the Day 1 requirement of getting the agent running with an Indian voice and successfully completing a basic conversation.

**Day 2 – Persona, Multilingual Interaction and Guardrails:**
Developed the agent's actual personality and responsibilities for Ratan Kirana & General Store. I defined its identity, objectives, knowledge boundaries, conversational style, multilingual/code-mixed interaction behaviour, and safety guardrails. The agent was instructed to handle catalogue and order-related conversations while avoiding unsupported claims such as inventing prices, order status, or delivery information. I also tuned the responses for voice interaction with shorter, more natural sentences and added appropriate escalation behaviour for out-of-scope requests. The Day 2 commit specifically introduced the structured identity, objectives, knowledge boundary, language guidance, guardrails and voice-friendly style.

**Day 3 – Personalised Frontend and Agent State:**
Built and personalised the frontend around the local-commerce experience instead of relying on the generic starter interface. I added the Ratan Kirana branding, catalogue, offers, product cards and Saathi agent panel, while implementing clear agent states such as ready, connecting, listening, speaking and call ended. The frontend was connected to the LiveKit agent so the complete flow could be tested from page load through conversation and call termination. This aligns with the Day 3 requirement to personalise the interface for the selected track and clearly communicate the agent's current state to the user. The Day 3 commit involved substantial frontend changes across the application shell, catalogue, offers, product cards, Saathi panel and related UI components.

**Day 4 – Persistent User Memory with SQLite:**
Implemented persistent customer memory so Saathi could remember returning callers instead of losing their information after every call. I introduced a **SQLite database** with a user profile schema containing the caller ID, name, language preference, customer facts and interaction timestamps. I added function tools for looking up and saving customer information, allowing the agent to retrieve a returning customer's previous information and greet them by name. I also implemented explicit consent before storing newly learned customer information, ensuring that the agent does not save personal facts without permission. The implementation was verified across calls so information could persist even after restarting the agent. This directly addresses the Day 4 challenge, which requires a database, lookup/save functions, returning-caller memory and consent-based saving.

**Day 5 – Real Data, Function Tools and Catalogue Integration:**
Extended the agent beyond static prompt knowledge by connecting it to actual domain data through function tools. For the Local Commerce track, I implemented catalogue and stock lookup functionality using a **SQLite-backed product database**, allowing Saathi to retrieve product information, prices and current stock instead of relying on hardcoded responses. I added tools for catalogue lookup and stock validation and connected these tools to the agent so it can decide when external data is required and call the appropriate function during a conversation. The backend also performs the required **server-side/database operations and API/tool calls** rather than exposing the data directly to the model. I added failure handling so tool/database failures produce a spoken fallback instead of silence or fabricated information, and the agent can use the returned data naturally in its response. This follows the Day 5 requirement to add a real domain-data function call, connect it to the agent, handle failures, and demonstrate the tool firing on a question that requires live/current catalogue information.


### How It Works

- **One task each day**, published here and announced to all participants
- **Pick a track on Day 1** and build for it all ten days
- **Post your progress on LinkedIn every day**, tagging Murf AI and using **#VoiceForBharat**
- **Ship a working, deployed agent by Day 10**

### Why Bharat

Most voice AI gets built for people who already have apps, data plans and English. This challenge is for the rest — the farmer checking a market rate before hiring a truck, the ASHA worker with forty households and no tooling, the family that needs a flood warning tonight.

Voice is the interface that works with **everyone**.

## Tracks

| Track | For |
|---|---|
| **Farm & Field** | Crop advisory, market prices, weather alerts, input costs |
| **Health Access** | Symptom triage, ASHA worker tools, medication reminders, scheme eligibility |
| **Learning & Literacy** | Voice tutoring for children and adult learners, spoken-English practice |
| **Local Commerce** | Order taking and catalogue tools for artisans, MSMEs, street vendors |
| **Financial Services** | Government scheme explainers, banking literacy, fraud awareness |
| **Disaster Response** | Flood and drought alerting, relief coordination, welfare check-ins |

## Quick Start

### Prerequisites

- A **Murf API account** — sign up at the [Murf API dashboard](https://murf.ai/api/dashboard) to get your API key
- Python 3.9+ with [uv](https://docs.astral.sh/uv/)
- [LiveKit Server](https://docs.livekit.io/transport/self-hosting/local/) for local development
- [LiveKit CLI](https://docs.livekit.io/intro/basics/cli/) (optional, recommended)

### Setup

1. **Fork and clone the [starter repository](https://github.com/murf-ai/murf-livekit-starter).**
2. **Install dependencies** and **copy the example environment file**, following the setup instructions in the starter.
3. **Add your API keys.** Create your Murf key from the [Murf API dashboard](https://murf.ai/api/dashboard) — the [quickstart](https://murf.ai/api/docs/introduction/quickstart#generate-an-api-key) walks you through it step by step.
4. **Run the agent** and talk to it.

You're not required to use the starter. Build in whatever language and framework you like — **using Murf Falcon for speech is the only requirement.**

## Daily Challenge Tasks

Each day you'll get a new task that builds on the agent you already have. The tasks are released here in the challenges folder.

**Stay tuned for daily task announcements!**

## Submitting Your Work

Each day:

1. **Build** the day's task in your fork.
2. **Record a short video** showing the specific thing that task asks for.
3. **Post it on LinkedIn**, tagging **Murf AI** and using **#VoiceForBharat**.

Your repo should tell the story by Day 10: a clear README, an honest known-limitations section, and a deployed agent someone can actually reach.

## Documentation & Resources

- [Murf LiveKit Starter](https://github.com/murf-ai/murf-livekit-starter) — the starter repo for this challenge
- [Murf API Dashboard](https://murf.ai/api/dashboard) — sign up and generate your API key
- [Murf API Quickstart](https://murf.ai/api/docs/introduction/quickstart#generate-an-api-key) — how to generate an API key, step by step
- [Murf API Documentation](https://murf.ai/api/docs/introduction/overview)
- [Falcon 2 Model Documentation](https://murf.ai/api/docs/text-to-speech-models/falcon-2)
- [Murf TTS Streaming Guide](https://murf.ai/api/docs/text-to-speech/streaming)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [LiveKit Telephony](https://docs.livekit.io/telephony/)
- [Backend Template](https://github.com/livekit-examples/agent-starter-python)
- [Frontend Template](https://github.com/livekit-examples/agent-starter-react)
- [LiveKit Agent Examples](https://github.com/livekit-examples/python-agents-examples)
- [Testing Voice Agents](https://docs.livekit.io/agents/start/testing/)

## License

Based on MIT-licensed templates from LiveKit, with Murf Falcon integration. See the LICENSE files for details.

---

**Ten days. One agent. Build something someone can actually use, and have fun while doing it!**

Built for #VoiceForBharat by [murf.ai](https://murf.ai/api)