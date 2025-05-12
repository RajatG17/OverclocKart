import { useState, useEffect } from "react";
import api from "../api";

interface Order { id: number; product_id: number; quantity: number; status: string}

export default function Orders() {
    const [orders, setOrders] = useState<Order[]>([]);

    useEffect(() => {
        api.get<Order[]>("/orders/${id}").then(res=> setOrders(res.data));
    }, []);

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">My Orders</h1>
            <ul className="list-disc pl-6">
                {orders.map(o => (
                    <li key={o.id}>
                        Order #{o.id} - Product {o.product_id} x{o.quantity} ({o.status})
                    </li>
                ))}
            </ul>
        </div>
    );
}