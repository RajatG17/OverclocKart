import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import Login from "./pages/Login";
import Products from "./pages/Products";
import React, { JSX } from "react";

function PrivateRoute({ children }: { children: JSX.Element }){
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/products" element={<PrivateRoute><Products /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/products" />} />
      </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App
