# LLM Code Deployment System

## Project Overview

This project implements a complete LLM-powered code generation and deployment pipeline. Students submit app briefs through an API, which automatically generates production-ready web applications, deploys them to GitHub Pages, and handles iterative updates through multiple evaluation rounds.

## System Architecture

The system consists of three main phases:

**Build Phase:** Receives app briefs, generates code using Gemini, deploys to GitHub Pages, and notifies evaluation endpoint

**Evaluate Phase:** Instructors run automated checks (static analysis, dynamic testing with Playwright, LLM-based code review)

**Revise Phase:** Students receive updated briefs to improve their apps, apply changes, and redeploy

## My Contributions

### Core Infrastructure

1. **Flask API Server (main.py)**
   - Implements `/api/deploy` endpoint to receive POST requests with app briefs
   - Validates incoming requests against student-provided secrets
   - Orchestrates the generation and deployment pipeline
   - Implements exponential backoff retry logic (1, 2, 4, 8 seconds) for evaluation URL notifications
   - Returns standardized HTTP responses with repo and deployment URLs
   - Handles both Round 1 (create) and Round 2+ (update) requests

2. **Code Generation Module (generator.py)**
   - Integrates with Gemini API to generate complete HTML5 applications
   - Implements fallback model selection (gemini-2.0-flash → gemini-1.5-pro → gemini-pro) for reliability
   - Decodes base64-encoded file attachments from data URIs
   - Generates professional README.md files with setup, usage, and code explanation sections
   - Automatically includes MIT LICENSE in all generated repos
   - Cleans up markdown formatting artifacts from LLM responses
   - Handles edge cases like missing attachments and API rate limiting

3. **GitHub Deployment Module (deployer.py)**
   - Creates public GitHub repositories with unique names based on task IDs
   - Implements smart repo management: creates new repos for Round 1, updates existing repos for Round 2+
   - Includes backwards compatibility to handle repos created with older naming schemes
   - Uploads multiple files to repos (index.html, README.md, LICENSE, attachments)
   - Enables GitHub Pages hosting via GitHub REST API
   - Retrieves commit SHA for verification and tracking
   - Constructs deployment URLs for student access and evaluation

### DevOps & Configuration

4. **Railway Deployment Configuration**
   - Configured Railway service with environment variables: GEMINI_API_KEY, GITHUB_TOKEN, MY_SECRET, PORT
   - Created Procfile with extended timeout (300 seconds) and 2 workers to handle long-running GitHub operations
   - Debugged and resolved worker timeout issues during file upload operations

### Integration & Testing

5. **End-to-End Testing**
   - Tested full deployment pipeline with multiple app types: Hello World, Calculator, Scientific Calculator, Snake Game
   - Verified Round 1 creation and Round 2 update workflows
   - Tested error handling and retry logic
   - Validated GitHub Pages hosting and accessibility
   - Confirmed attachment handling and file processing

## Technical Stack

- **Backend:** Python 3.13, Flask 3.0+
- **LLM Integration:** Google Gemini API (google-generativeai)
- **Version Control:** PyGithub for GitHub API interactions
- **Deployment:** Railway for API hosting
- **Hosting:** GitHub Pages for generated apps
- **HTTP Client:** requests library for evaluation URL notifications

## Key Features Implemented

- ✅ Secure request verification using student-provided secrets
- ✅ LLM-powered code generation with fallback models
- ✅ Automatic GitHub repo creation and management
- ✅ GitHub Pages deployment automation
- ✅ Round 1 (create) and Round 2+ (update) workflows
- ✅ Attachment decoding and inclusion in generated apps
- ✅ Exponential backoff retry logic for notifications
- ✅ Professional README generation
- ✅ MIT LICENSE inclusion
- ✅ Error handling and logging
- ✅ 30-second timeout extension for long-running operations

## API Endpoint

**URL:** `https://llm-deployment-api-production-e20d.up.railway.app/api/deploy`

**Health Check:** `https://llm-deployment-api-production-e20d.up.railway.app/health`

## Deployment Status

- **Status:** Production Ready
- **Server:** Railway (reliable-smile project)
- **Service:** llm-deployment-api-production (e20d)
- **GitHub Organization:** 24f2002696

## Testing Results

Successfully generated and deployed:
- Basic HTML pages (Hello World with styling)
- Calculator with basic arithmetic operations
- Scientific calculator with advanced math functions
- Snake game with interactive gameplay
- Multi-round updates (verified repo modification and redeployment)
