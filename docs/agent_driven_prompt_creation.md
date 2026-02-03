# Agent driven prompt creation

**The architecture bricks:**

**1. LangGraph agent in Cauldron**

Create a LangGraph workflow that handles the persona prompt analysis loop. This agent has:
- Node: Analyze prompt (LLM evaluates against persona quality criteria)
- Node: Generate feedback (LLM produces coaching feedback + probing questions)
- Node: Decide if ready (LLM determines if quality threshold met or needs more work)
- Conditional edge: Loop back to analyze if not ready, or exit if ready

State includes: current prompt version, analysis history, conversation turns.

**2. API endpoint in Cauldron**

Expose an endpoint that:
- Accepts: initial persona prompt + conversation history (if resuming)
- Streams back: agent feedback in real-time (as the LLM generates it)
- Returns: ready/not-ready status, structured feedback for UI rendering

Use Server-Sent Events (SSE) or WebSocket for streaming responses back to the UI.

**3. Integration point in Sociosim**

Add UI components:
- Input field for persona prompt (editable)
- Sidebar panel for agent conversation (displays streaming feedback)
- Button to submit prompt revision
- Visual indicator of quality/readiness status

On submit, call Cauldron endpoint, stream responses into sidebar, keep prompt editable.

**4. State management bridge**

The critical piece: conversation state lives in Cauldron (the LangGraph agent maintains it). Sociosim doesn't need to manage conversation history—it just sends the revised prompt + gets back feedback. Cauldron keeps the context across rounds.

**5. Handoff to BFF**

Once agent says "ready," that same endpoint returns the finalized persona prompt. Sociosim then calls the actual persona creation BFF endpoint to generate the full persona object.

**The flow in practice:**

User types prompt in Sociosim → clicks "Get feedback" → Sociosim calls `/analyze-persona-prompt` with prompt text → Cauldron's LangGraph agent analyzes, streams feedback back → Sociosim displays in sidebar as it arrives → User reads, edits prompt → Resubmits → Loop

**Key architectural decisions:**

- Agent state lives in Cauldron, not Sociosim (single source of truth)
- Streaming from Cauldron to Sociosim (real-time UX, not batch responses)
- Conversation history is part of LangGraph state (agent remembers context)
- Clear exit condition: agent signals "ready" and Sociosim switches modes (from feedback loop to persona creation)

Does that map to your existing repo structure?