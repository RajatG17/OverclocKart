import React from 'react';
import { useState } from 'react';
import { useAuth } from '../auth';
import { useNavigate } from 'react-router-dom';


export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async () => {
        try {
            await login(username, password);
            navigate("/products");
        }catch (err) {
            alert("Login failed");
        }
    };

    return (
        <div className="flex flex-col items-center mt-20">
            <h1 className="text-3x1 mb-6">Sign In</h1>

            <input className="border p-2 m-4 w-64"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)} />
            <input type="password"
                className="border p-2 mb-6 w-64"
                placeholder="Password"
                value={password}
                onChange={e => setPassword(e.target.value)} />
            <button className="bg-blue-600 text-white px-6 py-2 rounded"
                onClick={handleSubmit}>
                Log In
            </button>
        </div>
    );
}