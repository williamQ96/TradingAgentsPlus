# Development Log

... (previous entries)

### UI Redesign
- **3-Column Layout Implementation**:
    - **Config**: Dedicated left column for inputs.
    - **Feed**: Center column simplified to a pulse/status feed.
    - **Report Viewer**: New right column for full-height Markdown report reading.

### UI Redesign v0.3.0
- **3-Column Fixed Layout**:
    - **Config (Left)**: Fixed width (320px) column containing anchored branding and scrollable configuration form. Branding is permanently visible at the top.
    - **Live Intelligence (Center)**: Proportional width (40%) column for the streaming analysis feed.
    - **Report Viewer (Right)**: Flex-fill column maximizing space for reading detailed reports.
- **Styling Updates**:
    - Removed global header bar; integrated branding into the sidebar.
    - Unified vertical rhythm with full-height (`h-screen`) structure.
    - Added version number `0.3.0` to the brand header.

### UI Fixes v0.3.1
- **Branding**:
    - Reverted Logo text to "TA+".
    - Reverted Title to "TradingAgent Plus".
- **Feed & Interactivity**:
    - Fixed "System Processing" issue by correctly ensuring agent names and thought contents are mapped from the backend stream.
    - Added beautiful card styling for the feed with agent icons and proper name formatting.
    - Feed items are now interactive: clicking them opens the details in the Report Viewer.
- **Report Viewer**:
    - Fixed data connection so reports render correctly in Markdown.

### Feed Refinement v0.3.2
- **Agent Consolidation**:
    - The feed now maintains a single card per agent (Market, Social, System, etc.) and updates it in place when new information arrives, rather than creating a scroll-list of history.
- **Collapsible Cards**:
    - Cards are now **collapsed by default**, showing only the header (Icon/Name/Time).
    - Clicking a card expands it to reveal the thought process or detailed status.
    - "View Generated Report" button is hidden inside the collapsible body to reduce clutter.

### Debugging & Stability v0.3.3
- **Fixed "Stuck Processing" Bug**:
    - **Root Cause 1**: The frontend stream parser (`api.js`) was strictly expecting `\r\n\r\n` delimiters. If the backend sent standard `\n\n` or the connection closed with a partial buffer, the final "complete" event was ignored. Fixed by making the parser robust to any line endings and flushing remaining buffer on close.
    - **Root Cause 2**: Empty status updates (e.g. heartbeat or cleanup) were overwriting existing content in the feed cards with `undefined`, causing them to revert to a "Processing" state. Fixed `App.vue` to preserve existing content during updates.
    - **Root Cause 2**: Empty status updates (e.g. heartbeat or cleanup) were overwriting existing content in the feed cards with `undefined`, causing them to revert to a "Processing" state. Fixed `App.vue` to preserve existing content during updates.
    - **Root Cause 3**: The Feed UI (`AnalysisFeed.vue`) was showing a spinner whenever content was missing, regardless of whether the system had finished. Updated it to cease spinning and show "Completed" if the global status is complete.
    - **Root Cause 4 (Risk Agents)**: The specific "Risky", "Safe", and "Neutral" agents were updating a custom dictionary `risk_debate_state` instead of standard messages. The backend API wasn't looking inside this dictionary, so it sent empty events. Fixed `main.py` to extract their arguments.
    - **Root Cause 5 (Bull/Bear Agents)**: Similar to Risk agents, `Bull Researcher` and `Bear Researcher` updated `investment_debate_state`. Added logic to `main.py` to extract `current_response` from this state.
    - **Report Buttons for Debate Agents**: Updated the backend to classify debate outputs (Risk/Bull/Bear) as "Reports" internally. This triggers the frontend to show the cleaner "View Generated Report" button instead of displaying long raw text in the feed column.
    - **Risk Judge Fix**: Added specific logic to catch the `Judge` speaker and extract the `judge_decision` field, resolving the "I don't know what this means" error.
    - **Clean Feed Output**: Modified the Feed component to suppress the display of raw text if a "View Report" button is available, decluttering the interface effectively.
    - **Smart Spinner Logic**: Refactored the card display to be mutually exclusive: a card shows *either* the Report Button, *or* text content, *or* the "Processing" spinner. This prevents the confused UI state where a completed report button sat next to a processing spinner.
    - **Environment Restoration**: Fixed a missing `vite` binary issue by reinstalling frontend dependencies.
    - **Logic Correction**: Added missing `get_insider_sentiment` and `get_insider_transactions` tools to `news_analyst.py`, matching the functionality described in `strategys.md`.
    - **Logo Alignment**: Refined the CSS for the "TA+" logo to ensure perfect centering.
    - **Settings**: Added an "Interface Language" option (English/Chinese) to the Settings Modal, persisted via LocalStorage (UI only, translations pending).
    - **Documentation**: Updated `README.md` to highlight the new Vue.js GUI, Ollama support, and Multi-API features. Created `howto.md` with clear installation and startup instructions. Added `instruction.md` for user communication.
    - **Rebranding**: Renamed original documentation to `README_original.md` and established a new "TradingAgent Plus" `README.md` as the primary entry point, focusing on the enhanced features.
