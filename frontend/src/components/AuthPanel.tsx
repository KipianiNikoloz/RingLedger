import type { FormEvent } from "react";

import type { UserRole } from "../api/types";

interface AuthPanelProps {
  busy: boolean;
  currentRoleSummary: string;
  registerEmail: string;
  registerPassword: string;
  registerRole: UserRole;
  loginEmail: string;
  loginPassword: string;
  onRegisterEmailChange: (value: string) => void;
  onRegisterPasswordChange: (value: string) => void;
  onRegisterRoleChange: (value: UserRole) => void;
  onLoginEmailChange: (value: string) => void;
  onLoginPasswordChange: (value: string) => void;
  onRegister: (event: FormEvent<HTMLFormElement>) => void;
  onLogin: (event: FormEvent<HTMLFormElement>) => void;
}

export function AuthPanel({
  busy,
  currentRoleSummary,
  registerEmail,
  registerPassword,
  registerRole,
  loginEmail,
  loginPassword,
  onRegisterEmailChange,
  onRegisterPasswordChange,
  onRegisterRoleChange,
  onLoginEmailChange,
  onLoginPasswordChange,
  onRegister,
  onLogin,
}: AuthPanelProps): JSX.Element {
  return (
    <section className="panel auth-panel">
      <h2>Auth Session</h2>
      <p className="panel-note">Available tokens by role: {currentRoleSummary}</p>
      <div className="grid two-col">
        <form onSubmit={onRegister}>
          <h3>Register</h3>
          <label>
            Email
            <input
              name="register_email"
              type="email"
              value={registerEmail}
              onChange={(event) => onRegisterEmailChange(event.target.value)}
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
              required
            />
          </label>
          <label>
            Role
            <select value={registerRole} onChange={(event) => onRegisterRoleChange(event.target.value as UserRole)}>
              <option value="promoter">promoter</option>
              <option value="admin">admin</option>
              <option value="fighter">fighter</option>
              <option value="management">management</option>
            </select>
          </label>
          <button type="submit" disabled={busy} data-testid="register-submit">
            Register
          </button>
        </form>

        <form onSubmit={onLogin}>
          <h3>Login</h3>
          <label>
            Email
            <input
              name="login_email"
              type="email"
              value={loginEmail}
              onChange={(event) => onLoginEmailChange(event.target.value)}
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

