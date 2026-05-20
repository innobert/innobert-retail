#!/usr/bin/env python3
"""Seed script for testing: inserts clients and products into the project's SQLite DB.

Usage:
    python seed_db.py --clients 1000 --products 1000

Runs from repo root and writes directly into the application's database using
the same connection configuration as the app (via retail.nucleo.base_datos).
Products will use the default image name `default.png`.
"""
import argparse
import random
import time
from retail.nucleo import base_datos


def generate_clients(n, start_cedula=10000000, start_cel=300000000):
    # Nombres comunes en la costa colombiana
    first_names = [
        "Juan", "Carlos", "Andrés", "Luis", "José", "María", "Ana", "Carolina",
        "Valeria", "Daniel", "Esteban", "Natalia", "Camila", "Diego", "Sofía",
        "Anderson", "Yuri", "Jairo", "Rafael", "Omar"
    ]
    last_names = [
        "González", "Rodríguez", "Martínez", "Pérez", "Torres", "Ramírez", "Rojas",
        "Castillo", "Sánchez", "Díaz", "López", "Hernández"
    ]
    zonas = ["Barranquilla", "Cartagena", "Santa Marta", "Sincelejo", "Montería", "Buenaventura"]
    rows = []
    for i in range(n):
        idx = i + 1
        nombres = f"{random.choice(first_names)} {random.choice(first_names)}"
        apellidos = f"{random.choice(last_names)} {random.choice(last_names)}"
        cedula = start_cedula + i
        celular = start_cel + i
        zona = random.choice(zonas)
        rows.append((nombres, apellidos, cedula, celular, zona))
    return rows


def generate_products(n):
    product_names = [
        "Arepa de Huevo", "Arroz Diana 1kg", "Aceite Ideal 900ml", "Pasta Doria 500g",
        "Harina PAN 1kg", "Salchicha Ranchera", "Cerveza Águila 330ml", "Gaseosa Postobón 2L",
        "Leche Laive 1L", "Azúcar Morena 1kg", "Atún Van Camp 170g", "Café Sello Rojo 250g",
        "Pan Tajado Bimbo", "Galletas Festival", "Salsa Golf", "Mayonesa McCormick",
        "Refajo Colombiano", "Cerveza Club Colombia 330ml", "Pescado Empacado (congelado)",
        "Pastas Doria - Tallarín", "Arveja Liofilizada", "Pollo Empacado 1kg", "Queso costeño 500g",
        "Huevos docena", "Harina de Trigo 1kg", "Jugo Hit 1L", "Cereal Maíz 500g",
        "Detergente Ala 1kg", "Jabón en polvo", "Levadura"
    ]
    rows = []
    for i in range(n):
        idx = i + 1
        base_name = random.choice(product_names)
        producto = f"{base_name} - #{idx:04d}"
        # precio realista en pesos colombianos para productos de supermercado
        precio = random.randint(5000, 120000)
        # costo entre 60% y 85% del precio de venta
        costo = int(precio * random.uniform(0.6, 0.85))
        stock = random.randint(1, 300)
        estado = 1
        imagen = "default.png"
        rows.append((producto, precio, costo, stock, estado, imagen))
    return rows


def seed_database(clients=1000, products=1000, batch_size=500):
    start = time.time()
    print("Ensuring tables exist...")
    base_datos.create_tables()

    conn = base_datos.get_connection()
    cur = conn.cursor()

    print(f"Generating {clients} clientes...")
    client_rows = generate_clients(clients)
    print("Inserting clientes in transaction...")
    cur.executemany(
        "INSERT OR IGNORE INTO clientes (nombres, apellidos, cedula, celular, zona) VALUES (?, ?, ?, ?, ?)",
        client_rows,
    )

    print(f"Generating {products} productos...")
    product_rows = generate_products(products)
    print("Inserting productos in transaction...")
    cur.executemany(
        "INSERT OR IGNORE INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
        product_rows,
    )

    conn.commit()

    # report
    cur.execute("SELECT COUNT(*) FROM clientes")
    total_clients = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM inventario")
    total_products = cur.fetchone()[0]

    elapsed = time.time() - start
    print(f"Seed completed in {elapsed:.2f}s")
    print(f"Total clientes in DB: {total_clients}")
    print(f"Total productos in DB: {total_products}")

    # show a few samples
    cur.execute("SELECT id_cliente, nombres, apellidos, cedula FROM clientes ORDER BY id_cliente DESC LIMIT 5")
    print("Last 5 clientes:")
    for row in cur.fetchall():
        print(row)

    cur.execute("SELECT id_producto, producto, precio, stock, imagen FROM inventario ORDER BY id_producto DESC LIMIT 5")
    print("Last 5 productos:")
    for row in cur.fetchall():
        print(row)

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Seed DB with test clients and products")
    parser.add_argument("--clients", type=int, default=1000, help="Number of clientes to insert")
    parser.add_argument("--products", type=int, default=1000, help="Number of productos to insert")
    args = parser.parse_args()

    seed_database(clients=args.clients, products=args.products)


if __name__ == "__main__":
    main()
