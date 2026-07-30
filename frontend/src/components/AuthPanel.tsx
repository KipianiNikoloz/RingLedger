import type { FormEvent } from "react";

import type { UserRole } from "../api/types";

interface AuthPanelProps {
  busy: boolean;
  currentRoleSummary: string;
  registerEmail: string;
  registerPassword: string;
  provisionEmail: string;
  provisionPassword: string;
  provisionRole: Exclude<UserRole, "fighter">;
  loginEmail: string;
  loginPassword: string;
  onRegisterEmailChange: (value: string) => void;
  onRegisterPasswordChange: (value: string) => void;
  onProvisionEmailChange: (value: string) => void;
  onProvisionPasswordChange: (value: string) => void;
  onProvisionRoleChange: (value: Exclude<UserRole, "fighter">) => void;
  onLoginEmailChange: (value: string) => void;
  onLoginPasswordChange: (value: string) => void;
  onRegister: (event: FormEvent<HTMLFormElement>) => void;
  onProvision: (event: FormEvent<HTMLFormElement>) => void;
  onLogin: (event: FormEvent<HTMLFormElement>) => void;
}

export function AuthPanel({
  busy,
  currentRoleSummary,
  registerEmail,
  registerPassword,
  provisionEmail,
  provisionPassword,
  provisionRole,
  loginEmail,
  loginPassword,
  onRegisterEmailChange,
  onRegisterPasswordChange,
  onProvisionEmailChange,
  onProvisionPasswordChange,
  onProvisionRoleChange,
  onLoginEmailChange,
  onLoginPasswordChange,
  onRegister,
  onProvision,
  onLogin,
}: AuthPanelProps) {
  const tokenRoles = currentRoleSummary === "none" ? [] : currentRoleSummary.split(", ");

  return (
    <section className="panel auth-panel workflow-panel">
      <div className="panel-header">
        <h2>Auth Session</h2>
        <p className="panel-note">JWT tokens are stored in-memory by role for this session only.</p>
      </div>
      <div className="token-chip-row" aria-label="Available tokens by role">
        {tokenRoles.length > 0 ? (
          tokenRoles.map((role) => (
            <span className="token-chip" key={role}>
              {role}
            </span>
          ))
        ) : (
          <span className="token-chip token-chip-muted">none</span>
        )}
      </div>
      <div className="grid two-col">
        <form onSubmit={onRegister} className="form-panel">
          <h3>Register fighter</h3>
          <label>
            Email
            <input
              name="register_email"
              type="email"
              value={registerEmail}
              onChange={(event) => onRegisterEmailChange(event.target.value)}
              autoComplete="email"
              required
            />
          </label>
          <label>
            Password
            <input
              name="register_password"
              type="password"
              value={registerPassword}
              onChange={(event) => onRegisterPasswordChange(event.target.value)}
              autoComplete="new-password"
              required
            />
          </label>
          <button type="submit" disabled={busy} data-testid="register-submit">
            Register
          </button>
        </form>

        <form onSubmit={onProvision} className="form-panel">
          <h3>Provision privileged user</h3>
          <label>
            Email
            <input type="email" value={provisionEmail} onChange={(event) => onProvisionEmailChange(event.target.value)} required />
          </label>
          <label>
            Password
            <input type="password" value={provisionPassword} onChange={(event) => onProvisionPasswordChange(event.target.value)} required />
          </label>
          <label>
            Role
            <select value={provisionRole} onChange={(event) => onProvisionRoleChange(event.target.value as Exclude<UserRole, "fighter">)}>
              <option value="promoter">promoter</option>
              <option value="management">management</option>
              <option value="admin">admin</option>
            </select>
          </label>
          <button type="submit" disabled={busy}>Provision with admin token</button>
        </form>

        <form onSubmit={onLogin} className="form-panel">
          <h3>Login</h3>
          <label>
            Email
            <input
              name="login_email"
              type="email"
              value={loginEmail}
              onChange={(event) => onLoginEmailChange(event.target.value)}
              autoComplete="email"
              required
            />
          </label>
          <label>
            Password
            <input
              name="login_password"
              type="password"
              value={loginPassword}
              onChange={(event) => onLoginPasswordChange(event.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          <button type="submit" disabled={busy} data-testid="login-submit">
            Login
          </button>
        </form>
      </div>
    </section>
  );
}

