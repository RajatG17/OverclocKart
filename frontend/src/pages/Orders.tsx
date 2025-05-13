import { useState, useEffect } from "react";
import api from "../api";

interface Order { id: number; product_id: number; quantity: number; status: string}

export default function Orders() {
    const [orders, setOrders] = useState<Order[]>([]);

    useEffect(() => {
        api.get<Order[]>("/orders").then(res=> setOrders(res.data)).catch(console.error);
    }, []);

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">My Orders</h1>
            {orders.length === 0 && <p>No orders yet.</p>}
            <ul className="list-disc pl-6 space-y-2">
                {orders.map(o => (
                    <li key={o.id}>
                        Order #{o.id} - Product {o.product_id} x{o.quantity} (<em>{o.status}</em>)
                    </li>
                ))}
            </ul>
        </div>
    );
}