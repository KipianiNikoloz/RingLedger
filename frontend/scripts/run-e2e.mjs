import { spawn } from "node:child_process";
import http from "node:http";
import { fileURLToPath } from "node:url";
import { setTimeout as delay } from "node:timers/promises";

const host = "127.0.0.1";
const port = 4173;
const origin = `http://${host}:${port}`;
const rootDir = fileURLToPath(new URL("../", import.meta.url));
const viteBin = fileURLToPath(new URL("../node_modules/vite/bin/vite.js", import.meta.url));
const playwrightCli = fileURLToPath(new URL("../node_modules/playwright/cli.js", import.meta.url));

let server;

try {
  server = spawn(process.execPath, [viteBin, "--host", host, "--port", String(port)], {
    cwd: rootDir,
    env: { ...process.env, BROWSER: "none" },
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
  });
  server.stdout.on("data", drainServerOutput);
  server.stderr.on("data", drainServerOutput);

  await waitForServer(origin, server);
  const status = await runPlaywright();
  await stopServer(server);
  process.exit(status);
} catch (error) {
  await stopServer(server);
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
}

function drainServerOutput(chunk) {
  if (process.env.RINGLEDGER_E2E_SERVER_LOGS === "1") {
    process.stdout.write(chunk);
  }
}

async function waitForServer(url, child) {
  const deadline = Date.now() + 120_000;
  while (Date.now() < deadline) {
    if (child.exitCode !== null) {
      throw new Error(`Vite server exited before becoming ready with code ${child.exitCode}.`);
    }
    if (await canConnect(url)) {
      return;
    }
    await delay(250);
  }
  throw new Error(`Timed out waiting for Vite server at ${url}.`);
}

function canConnect(url) {
  return new Promise((resolve) => {
    const request = http.get(url, (response) => {
      response.resume();
      resolve(true);
    });
    request.setTimeout(750, () => {
      request.destroy();
      resolve(false);
    });
    request.on("error", () => resolve(false));
  });
}

function runPlaywright() {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [playwrightCli, "test", "--config=playwright.config.ts"], {
      cwd: rootDir,
      env: { ...process.env, RINGLEDGER_E2E_SERVER_MANAGED: "1" },
      stdio: "inherit",
      windowsHide: true,
    });
    child.on("exit", (code) => resolve(code ?? 1));
  });
}

async function stopServer(child) {
  if (!child || child.exitCode !== null) {
    return;
  }

  child.kill();
  const exited = await waitForExit(child, 2_000);
  if (exited) {
    return;
  }

  if (process.platform === "win32") {
    await runTaskkill(child.pid);
  } else {
    child.kill("SIGKILL");
  }
  await waitForExit(child, 2_000);
}

function waitForExit(child, timeoutMs) {
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      child.off("exit", onExit);
      resolve(false);
    }, timeoutMs);
    function onExit() {
      clearTimeout(timer);
      resolve(true);
    }
    child.once("exit", onExit);
  });
}

function runTaskkill(pid) {
  return new Promise((resolve) => {
    const killer = spawn("taskkill", ["/pid", String(pid), "/T", "/F"], {
      stdio: "ignore",
      windowsHide: true,
    });
    killer.on("exit", () => resolve());
  });
}
