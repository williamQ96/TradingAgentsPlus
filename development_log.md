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

## v0.4.0 - Rebranding & Polish
- **Web Title & Icon**:
    - Updated browser tab title to "TradingAgent Plus".
    - Replaced default Vite favicon with custom "TA+" logo (Green/White).
- **Versioning**: Bumped application version to v0.4.0 to reflect the major GUI and Feature upgrades.

## v0.5.0 - Functional Update: Ollama Integration
- **Ollama Integration**:
    - Analyzed Ollama directory structure.
    - Added a "Check Connection" button to the Settings Modal.
    - Implemented frontend status verification (`/v1/models` or `/api/tags`) to confirm local AI availability and list models.
    - Updated version to v0.5.0 (Functional Update).

## v0.6.0 - Functional Update: Ollama Management UI
- **Ollama Controls**:
    - Added **Context Length Slider** to Settings (Configurable from 4k to 256k, persisted in local storage).
    - Added **Model Management UI**: Input field with "Pull" and "Run" buttons for easy model management (Frontend implementation only; backend hooks pending).
    - Updated version to v0.6.0.

## v0.6.1 - UI Refinement: Stepped Context Slider
- **UI Update**:
    - Changed "Context Length" slider to use fixed steps: 4k, 8k, 16k, 32k, 64k, 128k, 256k.
    - Improved slider visual feedback with markers.
    - Updated version to v0.6.1.

## v0.7.0 - Functional Update: Ollama Backend Integration
- **Backend**:
    - Implemented `/api/ollama/manage` endpoint in `backend/main.py`.
    - Supports `pull` action: Triggers background Model Pull from Ollama URL (logs progress to backend console).
    - Supports `run` action: Triggers a lightweight Model Load (generate request) to ensure model is in memory.
- **Frontend**:
    - Connected "Pull" and "Run" buttons in Settings to the new backend API.
    - Added error handling and success alerts for model management actions.
    - Updated version to v0.7.0.

## v0.8.0 - Functional Update: Ollama Notification & Control
- **Backend Refinement**:
    - Added background task cancellation support for model pulling.
    - Implemented `/api/ollama/cancel` endpoint.
- **Frontend Refinement**:
    - **Notification Window**: Replaced standard alerts with a styled in-app processing window (Glassmorphism style).
    - **Progress Feedback**: Added spinner animation for "Pulling" and "Loading" states.
    - **Control**: Added **"Stop Process"** button to the notification window, allowing users to cancel a long-running model pull.
    - Updated version to v0.8.0.

## v0.8.1 - UI Update: Model Library Link
- **UI Refinement**:
    - Added a direct link to the **Ollama Model Library** (`ollama.com/search`) in the Model Management section to help users find compatible models.
    - Updated version to v0.8.1.

## v0.9.0 - Backend Logic Update: Robust Model Run
- **Backend**:
    - Enhanced `RUN` command logic.
    - Added pre-check: now queries `/api/ps` to check if a model is already loaded before attempting to run.
    - Improved error handling: catches connection errors and returns specific messages if Ollama is down or model load fails.
    - Returns specific success messages ("already running" vs "loaded successfully").
- **Versioning**:
    - Major functional update to backend logic > bumped to v0.9.0.

## v0.10.0 - Major Update: Real-time Pull Feedback
- **Backend Refinement**:
    - **Status Tracking**: Introduced active state tracking for Ollama model pulls (`pull_states`).
    - **Endpoint**: Added `GET /api/ollama/status/{model}` to expose real-time progress.
- **Frontend Refinement**:
    - **Smart Polling**: The notification window now automatically polls the backend for progress updates.
    - **Visual Feedback**:
        - Shows **Green Checkmark** and auto-stops spinner on success.
        - Shows **Red X** and specific error message on failure.
        - Shows **Cancel status** if manually stopped.
    - Resolves issue where spinner continued indefinitely after backend work finished.
    - Updated version to v0.10.0.

## v0.11.0 - UI Update: Final Report Visualization
- **Backend**:
    - Now streams a dedicated `Final Report` event after analysis generation is complete.
    - Sends the full comprehensive report content to the frontend feed.
- **Frontend (Analysis Feed)**:
    - Added special styling for the **"Final Report"** card.
    - Uses a **High-Contrast Dark Theme** (Stressed Color) to distinguish it from individual agent updates.
    - Displays a "View Comprehensive Analysis" button that opens the full report in the right-hand viewer.
    - Automatically highlights the final step of the process.
    - Updated version to v0.11.0.

## v0.11.1 - Hotfix: Final Report Generation
- **Backend Fix**:
    - Restored the missing `save_markdown_report` call which was causing a `NameError` and preventing the final report from being saved or streamed.
    - Result: Final Report Card now correctly generates and displays at the end of the analysis.
    - Updated version to v0.11.1.
