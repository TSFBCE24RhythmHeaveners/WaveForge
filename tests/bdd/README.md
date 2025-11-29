# BDD Tests for WaveForge Pro Hybrid Upload System

This directory contains Behavior-Driven Development (BDD) tests using **Behave** and **Playwright**.

## Overview

BDD tests are written in Gherkin syntax and provide human-readable test scenarios that describe application behavior from a user's perspective.

## Structure

```
tests/bdd/
├── features/               # Gherkin feature files
│   ├── online_recording.feature
│   ├── offline_recording.feature
│   ├── connection_loss.feature
│   ├── crash_recovery.feature
│   ├── performance.feature
│   └── ui_indicators.feature
├── steps/                  # Step definitions (Python + Playwright)
│   ├── online_recording_steps.py
│   ├── offline_recording_steps.py
│   ├── connection_loss_steps.py
│   └── common_steps.py
├── environment.py          # Behave hooks and Playwright setup
└── behave.ini             # Behave configuration
```

## Prerequisites

Install required dependencies:

```bash
# Install Behave and Playwright
pip install behave playwright pytest-playwright

# Install Playwright browsers
playwright install chromium
```

## Running Tests

### Run All BDD Tests
```bash
cd /Users/A3694852/Documents/dev/AI/Google/waveforge-pro
behave tests/bdd/features
```

### Run Specific Feature
```bash
behave tests/bdd/features/online_recording.feature
```

### Run Specific Scenario
```bash
behave tests/bdd/features/online_recording.feature:7
```

### Run with Tags
```bash
# Run only smoke tests (if tagged)
behave --tags=@smoke

# Exclude slow tests
behave --tags=~@slow
```

### Run in Headless Mode
```bash
HEADLESS=true behave tests/bdd/features
```

### Run with Video Recording
```bash
RECORD_VIDEO=true behave tests/bdd/features
```

### Generate JUnit Report
```bash
behave --junit --junit-directory=test-results/behave
```

## Features Covered

### 1. **Online Recording** (`online_recording.feature`)
- Record with active connection
- Real-time chunk upload
- Server-side assembly
- Fast save (<2 seconds)
- Server-backed playback
- Metadata preservation

### 2. **Offline Recording** (`offline_recording.feature`)
- Record without connection
- Local chunk storage
- Client-side assembly
- Local playback
- Upload when connection restored
- Automatic background upload queue

### 3. **Connection Loss** (`connection_loss.feature`)
- Seamless online→offline transition
- Partial upload handling
- Connection restoration during recording
- Multiple connection losses
- Network instability

### 4. **Crash Recovery** (`crash_recovery.feature`)
- Recovery after browser crash
- IndexedDB chunk recovery
- Upload or local assembly after recovery
- Multiple session recovery
- Partial recovery with corrupted data

### 5. **Performance** (`performance.feature`)
- Long recordings (1+ hours)
- Large file handling (500MB+)
- 100+ recordings in playlist
- Memory efficiency
- Concurrent operations
- Scalability scenarios

### 6. **UI Indicators** (`ui_indicators.feature`)
- Connection status display
- Server/Local badges
- Upload button visibility
- Progress indicators
- Toast notifications
- Loading states
- Error messages

## Test Scenarios

Total scenarios: **40+**

- ✅ Online recording flows: 7 scenarios
- ✅ Offline recording flows: 6 scenarios
- ✅ Connection loss handling: 7 scenarios
- ✅ Crash recovery: 9 scenarios
- ✅ Performance & scalability: 10 scenarios
- ✅ UI indicators & feedback: 15 scenarios

## Configuration

### Environment Variables

Set in `behave.ini` or via command line:

- `HEADLESS`: Run browser in headless mode (default: `true`)
- `BASE_URL`: Application URL (default: `http://localhost:8000`)
- `RECORD_VIDEO`: Record videos of test runs (default: `false`)

### Behave Configuration

See `behave.ini` for full configuration options:
- Output format: pretty with colors
- JUnit XML reports
- Timing information
- Verbose output

## Step Definitions

Step definitions use **Playwright** for browser automation:

```python
@when('the user clicks the record button')
def step_click_record(context):
    context.page.click('#recordBtn')
```

### Key Playwright Features Used:
- Page navigation and interaction
- Network request interception
- Offline mode simulation
- Console message capture
- Screenshot on failure
- Video recording (optional)

## Example Scenario

```gherkin
Scenario: Record audio with online connection
  Given the user has an active internet connection
  And the WaveForge Pro application is loaded
  When the user clicks the record button
  Then the recording indicator should be visible
  And chunks should be uploaded in real-time
```

## Debugging

### Run with Headed Browser
```bash
HEADLESS=false behave tests/bdd/features/online_recording.feature
```

### View Screenshots on Failure
Failed tests automatically generate screenshots in:
```
test-results/screenshots/
```

### View Videos (if enabled)
```
test-results/videos/
```

### Verbose Output
```bash
behave -v tests/bdd/features
```

### Stop on First Failure
```bash
behave --stop tests/bdd/features
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run BDD Tests
  run: |
    behave tests/bdd/features \
      --junit \
      --junit-directory=test-results/behave
  env:
    HEADLESS: true
    BASE_URL: http://localhost:8000

- name: Upload Test Results
  uses: actions/upload-artifact@v3
  with:
    name: bdd-test-results
    path: test-results/
```

## Best Practices

1. **Keep Scenarios Focused**: One behavior per scenario
2. **Use Background**: Share common setup steps
3. **Descriptive Names**: Clear scenario and step names
4. **Independent Tests**: No dependencies between scenarios
5. **Proper Cleanup**: Use `after_scenario` hooks
6. **Screenshots**: Automatically captured on failure
7. **Tag Organization**: Use tags for test categorization

## Tags

You can add tags to organize tests:

```gherkin
@smoke @critical
Scenario: Record audio with online connection
  ...
```

Run tagged tests:
```bash
behave --tags=@smoke
```

## Troubleshooting

### Playwright Not Found
```bash
pip install playwright
playwright install chromium
```

### Application Not Running
Ensure the server is running:
```bash
cd backend
python -m uvicorn app.server:app --reload
```

### Port Conflicts
Change BASE_URL if using different port:
```bash
BASE_URL=http://localhost:3000 behave tests/bdd/features
```

### Timeout Issues
Increase timeouts in step definitions:
```python
context.page.wait_for_selector('.element', timeout=10000)
```

## Contributing

When adding new scenarios:

1. Write feature file in `features/`
2. Implement steps in `steps/`
3. Run locally to verify
4. Update this README
5. Add to CI/CD pipeline

## Resources

- [Behave Documentation](https://behave.readthedocs.io/)
- [Playwright Python](https://playwright.dev/python/)
- [Gherkin Syntax](https://cucumber.io/docs/gherkin/)
- [BDD Best Practices](https://cucumber.io/docs/bdd/)
