import type { FormEvent } from "react";
import { useMemo, useState } from "react";

import { createPrivilegedUser, loginUser, registerUser } from "../api/client";
import type { UserRole } from "../api/types";
import { decodeRoleFromJwt } from "../auth";

interface AuthWorkflowOptions {
  runAction: (label: string, callback: () => Promise<void>) => Promise<void>;
  pushLog: (message: string) => void;
}

export interface AuthWorkflowModel {
  registerEmail: string;
  registerPassword: string;
  registerResult: unknown;
  provisionEmail: string;
  provisionPassword: string;
  provisionRole: Exclude<UserRole, "fighter">;
  loginEmail: string;
  loginPassword: string;
  currentRoleSummary: string;
  promoterToken: string | undefined;
  fighterToken: string | undefined;
  adminToken: string | undefined;
  setRegisterEmail: (value: string) => void;
  setRegisterPassword: (value: string) => void;
  setProvisionEmail: (value: string) => void;
  setProvisionPassword: (value: string) => void;
  setProvisionRole: (value: Exclude<UserRole, "fighter">) => void;
  setLoginEmail: (value: string) => void;
  setLoginPassword: (value: string) => void;
  handleRegister: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleProvision: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleLogin: (event: FormEvent<HTMLFormElement>) => Promise<void>;
}

export function useAuthWorkflow({ runAction, pushLog }: AuthWorkflowOptions): AuthWorkflowModel {
  const [registerEmail, setRegisterEmail] = useState("promoter.frontend@example.com");
  const [registerPassword, setRegisterPassword] = useState("PromoterPass123!");
  const [registerResult, setRegisterResult] = useState<unknown>(null);
  const [provisionEmail, setProvisionEmail] = useState("promoter.ops@example.com");
  const [provisionPassword, setProvisionPassword] = useState("PromoterPass123!");
  const [provisionRole, setProvisionRole] = useState<Exclude<UserRole, "fighter">>("promoter");

  const [loginEmail, setLoginEmail] = useState("promoter.frontend@example.com");
  const [loginPassword, setLoginPassword] = useState("PromoterPass123!");
  const [tokensByRole, setTokensByRole] = useState<Partial<Record<UserRole, string>>>({});

  const currentRoleSummary = useMemo(() => {
    const registeredRoles = Object.entries(tokensByRole)
      .filter((entry): entry is [UserRole, string] => typeof entry[1] === "string")
      .map(([role]) => role)
      .sort()
      .join(", ");
    return registeredRoles.length > 0 ? registeredRoles : "none";
  }, [tokensByRole]);

  async function handleRegister(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    await runAction("register", async () => {
      const response = await registerUser({
        email: registerEmail,
        password: registerPassword,
      });
      setRegisterResult(response);
    });
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    await runAction("login", async () => {
      const response = await loginUser({ email: loginEmail, password: loginPassword });
      const role = decodeRoleFromJwt(response.access_token);
      if (role === null) {
        throw new Error("Could not decode role from JWT.");
      }
      setTokensByRole((previous) => ({ ...previous, [role]: response.access_token }));
      pushLog(`token stored for role=${role}`);
    });
  }

  async function handleProvision(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    await runAction("provision user", async () => {
      const adminToken = tokensByRole.admin;
      if (!adminToken) {
        throw new Error("Log in as an admin before provisioning privileged users.");
      }
      const response = await createPrivilegedUser(adminToken, {
        email: provisionEmail,
        password: provisionPassword,
        role: provisionRole,
      });
      setRegisterResult(response);
    });
  }

  return {
    registerEmail,
    registerPassword,
    registerResult,
    provisionEmail,
    provisionPassword,
    provisionRole,
    loginEmail,
    loginPassword,
    currentRoleSummary,
    promoterToken: tokensByRole.promoter,
    fighterToken: tokensByRole.fighter,
    adminToken: tokensByRole.admin,
    setRegisterEmail,
    setRegisterPassword,
    setProvisionEmail,
    setProvisionPassword,
    setProvisionRole,
    setLoginEmail,
    setLoginPassword,
    handleRegister,
    handleProvision,
    handleLogin,
  };
}

