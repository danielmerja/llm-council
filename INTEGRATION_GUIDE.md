# Integration Guide - Merging PRs from karpathy/llm-council

## Overview

This guide provides step-by-step instructions for integrating the best PRs from karpathy/llm-council into danielmerja/llm-council. We've created separate evaluation branches for each tier to test in isolation.

## Evaluation Branches Created

We've created 5 evaluation branches to test different PR categories:

```
eval/tier1-critical-fixes      - Simple bug fixes (PR #72, #71, #51)
eval/tier2-ollama-support      - Local model support (PR #76)
eval/tier2-docker-support      - Docker deployment (PR #53)
eval/tier2-ux-improvements     - UX enhancements (PR #69, #67)
eval/tier3-testing             - Test infrastructure (PR #24)
```

---

## 🚀 Phase 1: Critical Fixes (Quick Wins)

### Branch: `eval/tier1-critical-fixes`

**Target PRs:** #72 (title fix), #71 (typo fix), #51 (API validation)

#### Step 1: PR #72 - Fix Hardcoded Title Model

**Problem:** `backend/storage.py` hardcodes `google/gemini-2.5-flash` for title generation.

**Files:** [PR #72 on GitHub](https://github.com/karpathy/llm-council/pull/72)

```bash
# Switch to evaluation branch
git checkout eval/tier1-critical-fixes

# Fetch the PR
git fetch karpathy pull/72/head:pr-72

# Cherry-pick the commit
git cherry-pick pr-72

# Alternatively, manual fix:
# Edit backend/storage.py, line ~50:
# Change: model="google/gemini-2.5-flash"
# To:     model=CHAIRMAN_MODEL
```

**Manual Fix (if cherry-pick fails):**
```python
# backend/storage.py
from .config import CHAIRMAN_MODEL  # Add this import if not present

# In generate_conversation_title() function:
response = await query_model(
    model=CHAIRMAN_MODEL,  # Changed from "google/gemini-2.5-flash"
    messages=[{"role": "user", "content": prompt}]
)
```

**Testing:**
```bash
# Start the app
cd /home/runner/work/llm-council/llm-council
./start.sh

# In browser:
# 1. Start a new conversation
# 2. Send a message
# 3. Verify conversation gets a title (check sidebar)
# 4. No errors in console/terminal
```

---

#### Step 2: PR #71 - Fix README Typos

**Files:** [PR #71 on GitHub](https://github.com/karpathy/llm-council/pull/71)

```bash
git fetch karpathy pull/71/head:pr-71
git cherry-pick pr-71

# Or manually review and apply typo fixes to README.md
```

**Testing:** Review README.md renders correctly on GitHub.

---

#### Step 3: PR #51 - API Key Validation

**Files:** [PR #51 on GitHub](https://github.com/karpathy/llm-council/pull/51)

```bash
git fetch karpathy pull/51/head:pr-51
git cherry-pick pr-51
```

**Manual Fix:**
```python
# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY is not set. "
        "Please create a .env file with your API key: "
        "OPENROUTER_API_KEY=sk-or-v1-..."
    )
```

**Testing:**
```bash
# Test 1: Missing API key
mv .env .env.backup
python -m backend.main
# Should see: "ValueError: OPENROUTER_API_KEY is not set..."

# Test 2: Valid API key
mv .env.backup .env
python -m backend.main
# Should start normally
```

---

#### Commit Tier 1 Changes

```bash
# If all tests pass, merge to main branch
git checkout copilot/review-main-pull-requests
git merge eval/tier1-critical-fixes --no-ff -m "Integrate Tier 1 critical fixes from karpathy/llm-council"
```

---

## 🌟 Phase 2A: Ollama Support (Local Models)

### Branch: `eval/tier2-ollama-support`

**Target PR:** #76 - Multi-provider support

**This is the biggest value-add** - enables running models locally without API keys.

#### Understanding PR #76

**What it does:**
- Adds provider abstraction layer (`backend/providers/`)
- Supports 3 modes: OpenRouter-only, Ollama-only, Mixed
- Backward compatible with existing configs
- Uses factory pattern for clean architecture

**New Structure:**
```
backend/providers/
├── base.py              # Abstract base provider
├── factory.py           # Provider factory
├── openrouter.py        # OpenRouter implementation
└── ollama.py            # Ollama implementation (NEW)
```

#### Integration Steps

```bash
git checkout eval/tier2-ollama-support

# Fetch PR #76
git fetch https://github.com/maeste/llm-council.git ollama:pr-76
git merge pr-76 --no-ff
```

**If merge conflicts occur:**
1. The PR refactors `backend/openrouter.py` into provider structure
2. Resolve by accepting PR changes (they include all existing functionality)
3. Check that `backend/council.py` imports are updated correctly

**Configuration:**

Create/update `.env`:
```bash
# Mode 1: OpenRouter only (default, existing behavior)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...

# Mode 2: Ollama only (fully local, no API key)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

# Mode 3: Mixed (some models local, some cloud)
LLM_PROVIDER=mixed
OPENROUTER_API_KEY=sk-or-v1-...
OLLAMA_BASE_URL=http://localhost:11434

# Council configuration with prefixes
COUNCIL_MODELS=ollama:llama2,ollama:mistral,openrouter:google/gemini-pro
CHAIRMAN_MODEL=openrouter:anthropic/claude-3-opus
```

#### Testing PR #76

**Test 1: OpenRouter Mode (Backward Compatibility)**
```bash
# .env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
COUNCIL_MODELS=openai/gpt-4,google/gemini-pro,anthropic/claude-3
CHAIRMAN_MODEL=google/gemini-2.0-flash-thinking-exp:free

# Start app
./start.sh

# In browser:
# 1. Send test message
# 2. Verify all 3 stages complete
# 3. Check all models respond
```

**Test 2: Ollama Mode (Local)**

Prerequisites:
```bash
# Install Ollama (if not already)
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama2
ollama pull mistral
ollama pull phi
```

Configuration:
```bash
# .env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
COUNCIL_MODELS=llama2,mistral,phi
CHAIRMAN_MODEL=llama2
```

Test:
```bash
./start.sh

# In browser:
# 1. Send message: "What is 2+2?"
# 2. Verify responses from local models
# 3. Check terminal - should see Ollama API calls
# 4. No OpenRouter API calls should occur
```

**Test 3: Mixed Mode**
```bash
# .env
LLM_PROVIDER=mixed
OPENROUTER_API_KEY=sk-or-v1-...
OLLAMA_BASE_URL=http://localhost:11434
COUNCIL_MODELS=ollama:llama2,ollama:mistral,openrouter:google/gemini-pro
CHAIRMAN_MODEL=openrouter:google/gemini-2.0-flash-thinking-exp:free

# Test that both providers work together
./start.sh
```

#### Troubleshooting

See `TROUBLESHOOTING.md` added by PR #76 for common issues:
- Ollama connection refused
- Model not found errors
- API key errors in mixed mode

---

## 🐳 Phase 2B: Docker Support

### Branch: `eval/tier2-docker-support`

**Target PR:** #53 - Docker container setup

```bash
git checkout eval/tier2-docker-support

# Fetch PR #53
git fetch https://github.com/Aeliot-Tm/llm-council.git docker:pr-53
git merge pr-53 --no-ff
```

**What's Added:**
- `Dockerfile` - Multi-stage build
- `docker-compose.yml` - Easy orchestration
- `.dockerignore` - Optimized build context
- `docker/` directory - Helper scripts

**Testing:**

```bash
# Build and run
docker-compose up --build

# Verify:
# - Frontend accessible at http://localhost:5173
# - Backend accessible at http://localhost:8001
# - Data persists in Docker volume

# Test data persistence
docker-compose down
docker-compose up
# Previous conversations should still exist
```

**Production Deployment:**
```bash
# Build for production
docker build -t llm-council:latest .

# Run with custom env
docker run -d \
  -p 8001:8001 \
  -e OPENROUTER_API_KEY=sk-or-v1-... \
  -v llm-council-data:/app/data \
  llm-council:latest
```

---

## 🎨 Phase 2C: UX Improvements

### Branch: `eval/tier2-ux-improvements`

**Target PRs:** #69 (prevent switching), #67 (continuous conversation)

#### PR #69: Prevent Conversation Switching During Streaming

```bash
git checkout eval/tier2-ux-improvements

# Fetch and merge PR #69
git fetch https://github.com/harshbopaliya/llm-council.git feat/prevent-conversation-switch-while-loading:pr-69
git merge pr-69 --no-ff
```

**What it does:**
- Disables sidebar conversation switching while response is loading
- Disables "New Conversation" button during streaming
- Adds visual indicator
- Shows tooltip explaining why disabled

**Testing:**
1. Start conversation
2. Send message
3. While response is streaming, try to:
   - Click other conversations (should be disabled)
   - Click "New Conversation" (should be disabled)
4. Wait for completion
5. Verify controls re-enabled

#### PR #67: Continuous Conversation Mode

```bash
# Fetch and merge PR #67
git fetch https://github.com/Vijay-48/llm-council.git feature/continuous-conversation:pr-67
git merge pr-67 --no-ff
```

**What it does:**
- Input form always visible (doesn't disappear after sending)
- Draft mode: conversation only created when first message sent
- No more empty conversations in history

**Testing:**
1. Load app (don't send message yet)
2. Verify no conversation in sidebar
3. Send message
4. Conversation appears in sidebar with generated title
5. Input form stays visible
6. Send another message
7. Same conversation continues
8. Check storage - no empty conversations

---

## 🧪 Phase 3: Testing Infrastructure

### Branch: `eval/tier3-testing`

**Target PR:** #24 - Comprehensive test suite

⚠️ **Recommendation:** Do this LAST after all features are stable.

```bash
git checkout eval/tier3-testing

# Fetch PR #24
git fetch https://github.com/domfahey/llm-council.git add-tests:pr-24
git merge pr-24 --no-ff
```

**What's Added:**
- `tests/` directory with 53 tests
- `pytest.ini` configuration
- `.github/workflows/` CI configuration
- `ruff`, `black`, `mypy` configurations
- Security best practices

**Dependencies Added:**
```bash
# Install test dependencies
uv pip install pytest pytest-asyncio pytest-cov httpx ruff black mypy
```

**Running Tests:**
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html

# Run linting
uv run ruff check backend/
uv run black --check backend/
uv run mypy backend/
```

**Expected Results:**
- 53 tests pass
- 86% code coverage
- No linting errors
- Type checking passes

---

## 📋 Final Integration Checklist

Before merging each evaluation branch to main:

- [ ] All tests pass (or N/A if no tests yet)
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] Basic conversation flow works end-to-end
- [ ] No console errors in browser
- [ ] No errors in terminal logs
- [ ] Configuration options work as documented
- [ ] Existing features still work (backward compatibility)
- [ ] Documentation updated (README, etc.)
- [ ] Security scan passes (no new vulnerabilities)

---

## 🔄 Recommended Merge Order

1. **Week 1:** `eval/tier1-critical-fixes` → `main`
   - Low risk, immediate value
   - Foundation for other changes

2. **Week 2:** `eval/tier2-ollama-support` → `main`
   - Biggest feature addition
   - Test thoroughly with different provider modes
   - Update documentation

3. **Week 3:** `eval/tier2-docker-support` → `main`
   - Makes deployment easier
   - Test on different platforms

4. **Week 3:** `eval/tier2-ux-improvements` → `main`
   - Polish the user experience
   - May need resolution if conflicts with Ollama PR

5. **Week 4:** `eval/tier3-testing` → `main`
   - Ensure codebase stability
   - Set up CI/CD

---

## 🔧 Handling Conflicts

**Common Conflict Scenarios:**

### Scenario 1: Provider refactoring conflicts

**If PR #76 (Ollama) conflicts with other PRs:**
- Accept PR #76's provider structure
- Re-apply other changes on top of new structure
- Update imports if needed

### Scenario 2: Frontend component conflicts

**If UI PRs conflict:**
- Merge in order: #69 → #67
- Resolve by keeping both features
- Test interaction between features

### Scenario 3: Configuration conflicts

**If .env or config.py conflicts:**
- Keep all configuration options from all PRs
- Document new options in README
- Provide sensible defaults

---

## 📊 Testing Matrix

After integration, test all combinations:

| Provider Mode | Docker | UI Features | Status |
|--------------|--------|-------------|--------|
| OpenRouter   | No     | Basic       | ✅     |
| OpenRouter   | Yes    | Basic       | ⏳     |
| Ollama       | No     | Basic       | ⏳     |
| Ollama       | Yes    | Basic       | ⏳     |
| Mixed        | No     | Enhanced    | ⏳     |
| Mixed        | Yes    | Enhanced    | ⏳     |

---

## 🚨 Rollback Plan

If any integration causes issues:

```bash
# Rollback specific branch
git checkout main
git revert --no-commit <merge-commit-hash>..HEAD
git commit -m "Rollback [feature] due to [issue]"

# Or reset to before merge
git reset --hard <commit-before-merge>
git push --force origin main  # ⚠️ Use with caution

# Better: Keep broken branch, fix forward
git checkout eval/tier2-ollama-support
git revert <problematic-commit>
# Fix and re-merge
```

---

## 📝 Documentation Updates

After each successful integration, update:

1. **README.md**
   - New features
   - New configuration options
   - Updated setup instructions

2. **CLAUDE.md** (if exists)
   - Architecture changes
   - New modules/patterns
   - Migration notes

3. **CHANGELOG.md** (create if doesn't exist)
   - Version bumps
   - New features
   - Bug fixes
   - Breaking changes

---

## 🎯 Success Criteria

**Minimum Success:**
- Tier 1 fixes integrated and working
- No regressions in existing functionality
- Documentation updated

**Full Success:**
- All Tier 1 & 2 features integrated
- Multiple provider modes working
- Docker deployment functional
- UX improvements live
- Test suite passing

**Excellence:**
- All above ✅
- Test suite integrated with 85%+ coverage
- CI/CD pipeline running
- Performance benchmarks documented
- User feedback collected and addressed

---

## 🔗 Quick Reference Links

- [PR Review Analysis](./PR_REVIEW_ANALYSIS.md)
- [karpathy/llm-council PRs](https://github.com/karpathy/llm-council/pulls)
- [Evaluation Branches in your fork](https://github.com/danielmerja/llm-council/branches/all?query=eval%2F)

---

## 💡 Tips & Tricks

1. **Use `git worktree` for parallel testing:**
   ```bash
   git worktree add ../llm-council-eval-tier1 eval/tier1-critical-fixes
   git worktree add ../llm-council-eval-tier2 eval/tier2-ollama-support
   # Test both simultaneously in different directories
   ```

2. **Create test scripts:**
   ```bash
   # test-integration.sh
   #!/bin/bash
   echo "Starting backend..."
   ./start.sh &
   BACKEND_PID=$!
   sleep 5
   
   # Run your tests
   curl http://localhost:8001/health
   
   kill $BACKEND_PID
   ```

3. **Document everything:**
   Keep notes on what works, what doesn't, and why. This helps if you need to rollback or debug later.

4. **Small commits:**
   Commit after each PR integration with clear messages:
   ```
   feat: Add Ollama provider support from PR #76
   fix: Resolve merge conflict in config.py
   test: Verify Ollama mode works with local models
   ```

---

## ❓ FAQ

**Q: Should I merge all PRs at once?**
A: No! Test each tier separately. Only merge once thoroughly tested.

**Q: What if a PR breaks existing functionality?**
A: Document the issue, try to fix it, or skip that PR for now. Don't merge broken code.

**Q: Can I modify the PRs?**
A: Yes! You can cherry-pick specific commits or modify code to fit your needs.

**Q: What about security?**
A: Run `uv run pip-audit` after each integration to check for vulnerabilities.

**Q: How do I handle upstream updates?**
A: Periodically fetch from karpathy remote and review new commits/PRs.

---

## 📮 Getting Help

If you encounter issues:
1. Check the PR discussion on GitHub
2. Review the original PR author's README/docs
3. Test in a clean environment
4. Document your issue and seek help from the community

Good luck with the integration! 🚀
