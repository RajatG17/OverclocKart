import { createContext, useContext, useState, ReactNode } from "react";
import api from "./api";
import React from "react";


interface AuthContextType {
    token: string | null;
    role: string | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const useAuth = () => useContext(AuthContext);

export function AuthProvider ({ children }: { children: ReactNode }) {
    const [token, setToken] = useState(localStorage.getItem("token"));
    const [role, setRole] = useState(localStorage.getItem("role"));

    const login = async (username: string, password: string) => {
        const { data } = await api.post("/auth/login", { username, password });
        setToken(data.access_token);
        const payload = JSON.parse(atob(data.access_token.split(".")[1]));
        setRole(payload.role);
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", payload.role);
    };

    const logout = () => {
        setToken(null);
        setRole(null);
        localStorage.removeItem("token");
        localStorage.removeItem("role");
    };

    return (
        <AuthContext.Provider value={{ token, role, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

