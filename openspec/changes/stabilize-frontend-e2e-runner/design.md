## Context

`frontend/playwright.config.ts` currently lets Playwright own Vite startup through `webServer`. On this Windows workspace the browser test completes successfully, then Playwright waits until global timeout while tearing down the setup plugin. The underlying app journey is good, but the command is not a trustworthy gate.

## Goals / Non-Goals

**Goals:**
- Make `npm run test:e2e` exit with Playwright's actual test result.
- Keep the browser journey and mocked API contracts unchanged.
- Clean up only the Vite child process started by the runner.

**Non-Goals:**
- No new browser-test framework or runtime dependency.
- No change to application behavior, API mocks, or visual design.
- No change to backend test commands.

## Decisions

1. **Move server ownership to an npm runner script.** The script starts Vite directly with Node, waits for `http://127.0.0.1:4173`, then invokes Playwright. This avoids Playwright's Windows web-server teardown path. Alternative considered: keep `webServer` and increase timeouts; rejected because it hides the hang instead of fixing the gate.

2. **Use built-in Node APIs only.** The runner uses `child_process`, `http`, and `process` APIs already available in the frontend toolchain. Alternative considered: add a helper dependency such as `start-server-and-test`; rejected to keep the frontend dependency surface stable.

3. **Force-clean the started process tree on Windows.** If normal child termination does not exit promptly, the runner calls `taskkill` for the child PID. Alternative considered: leave cleanup to Playwright; rejected because that is the failing path.

## Risks / Trade-offs

- [Risk] A pre-existing process already owns port 4173. -> Mitigation: the runner fails fast with a clear startup error instead of reusing unknown servers.
- [Risk] Forced cleanup could kill the wrong process. -> Mitigation: cleanup targets only the child PID started by the runner.
