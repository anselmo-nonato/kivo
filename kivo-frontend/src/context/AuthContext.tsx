"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

export interface WorkspaceBrief {
  id: string;
  name: string;
  type: "solo" | "family";
  role: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  mfa_enabled: boolean;
  workspaces: WorkspaceBrief[];
}

interface AuthContextType {
  user: User | null;
  activeWorkspace: WorkspaceBrief | null;
  isLoading: boolean;
  loginWithTokens: (accessToken: string, refreshToken: string, userData: User) => void;
  logout: () => void;
  setActiveWorkspaceId: (workspaceId: string) => void;
  reloadUserData: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [activeWorkspace, setActiveWorkspace] = useState<WorkspaceBrief | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();

  const reloadUserData = async () => {
    try {
      const res = await api.get("/auth/me");
      setUser(res.data);
      localStorage.setItem("kivo_user", JSON.stringify(res.data));

      // Define workspace ativo
      if (res.data.workspaces && res.data.workspaces.length > 0) {
        const savedWsId = localStorage.getItem("kivo_active_workspace_id");
        const found = res.data.workspaces.find((w: WorkspaceBrief) => w.id === savedWsId);
        const wsToSet = found || res.data.workspaces[0];
        setActiveWorkspace(wsToSet);
        localStorage.setItem("kivo_active_workspace_id", wsToSet.id);
      }
    } catch (err) {
      logout();
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("kivo_access_token");
    if (token) {
      reloadUserData().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const loginWithTokens = (accessToken: string, refreshToken: string, userData: User) => {
    localStorage.setItem("kivo_access_token", accessToken);
    localStorage.setItem("kivo_refresh_token", refreshToken);
    localStorage.setItem("kivo_user", JSON.stringify(userData));
    setUser(userData);

    if (userData.workspaces && userData.workspaces.length > 0) {
      const initialWs = userData.workspaces[0];
      setActiveWorkspace(initialWs);
      localStorage.setItem("kivo_active_workspace_id", initialWs.id);
    }
    router.push("/dashboard");
  };

  const logout = () => {
    localStorage.removeItem("kivo_access_token");
    localStorage.removeItem("kivo_refresh_token");
    localStorage.removeItem("kivo_user");
    localStorage.removeItem("kivo_active_workspace_id");
    setUser(null);
    setActiveWorkspace(null);
    router.push("/login");
  };

  const setActiveWorkspaceId = (workspaceId: string) => {
    if (!user) return;
    const ws = user.workspaces.find((w) => w.id === workspaceId);
    if (ws) {
      setActiveWorkspace(ws);
      localStorage.setItem("kivo_active_workspace_id", ws.id);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        activeWorkspace,
        isLoading,
        loginWithTokens,
        logout,
        setActiveWorkspaceId,
        reloadUserData,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de um AuthProvider");
  }
  return context;
};
