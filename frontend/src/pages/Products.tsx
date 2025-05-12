import React from 'react';
import { useState, useEffect } from 'react';
import api from "../api";
import { useAuth } from '../auth';

interface Product { id: number; name: string; price: number;}

export default function Products() {
    const [products, setProducts] = useState<Product[]>([]);
    const { role } = useAuth();

    useEffect(() => {
        api.get<Product[]>("/products").then(res => setProducts(res.data));
    }, []);

    const addProduct = async () => {
        const name = prompt("Product name?");
        const price = prompt("Price?");
        if (!name || !price) return;
        await api.post("/products", { name, price: Number(price) });
        const res = await api.get<Product[]>("/products");
        setProducts(res.data);
    };

    const buy = async (id: number) => {
        await api.post("/orders", { product_id: id, quantity: 1 });
        alert("Order placed!");
    };

    return (
        <div className="p-6">
            {/* <h1 className="text-2xl font-hold">Products Page</h1>
            <p>TODO: implement product listing here.</p> */}
            <div className="flex justify-between items-center mb-4">
                <h1 className='text-2xl font-bold'>Products</h1>
                {role === "admin" && (
                    <button 
                    className="bg-green-600 text-white px-3 py-1 rounded"
                    onClick={addProduct}
                    > + Add </button>
                )}
            </div>
            <div className="grid grid-cols-2 gap-6">
                {products.map(p=> (
                    <div
                    key={p.id}
                    className="border rounded p-4 shadow flex flex-col"
                    >
                        <h2 className="font-semibold mb-2">{p.name}</h2>
                        <p className="mb-4">${p.price.toFixed(2)}</p>
                        <button
                        className="mt-auto bg-blue-600 text-white px-2 py-1 rounded"
                        onClick={() => buy(p.id)}
                        >Buy</button>
                    </div>    
                ))}
            </div>
            
        </div>
    );
}