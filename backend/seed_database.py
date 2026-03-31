#!/usr/bin/env python3
"""
Database seeding script for Vintique PostgreSQL
Run this script to populate your database with initial sample data
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, engine
from app.models import User, Account, Product, Cart, Order, Transaction, Guest
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

def seed_database():
    """Seed the database with initial sample data"""
    
    db = SessionLocal()
    try:
        print("🌱 Starting database seeding...")
        
        # Create sample users
        print("👥 Creating sample users...")
        
        # Admin user
        admin_user = User(
            email="admin@vintique.com",
            username="admin",
            password=get_password_hash("admin123"),
            shipping_address="123 Admin St, City, State 12345",
            is_admin=True,
            status="active"
        )
        db.add(admin_user)
        db.flush()  # Get the ID
        
        # Create admin account
        admin_account = Account(
            user_id=admin_user.id,
            balance=Decimal("10000.00")
        )
        db.add(admin_account)
        
        # Regular users
        users_data = [
            {
                "email": "john@example.com",
                "username": "john_doe",
                "password": "password123",
                "shipping_address": "456 Oak Ave, Town, State 67890",
                "balance": Decimal("1500.00")
            },
            {
                "email": "jane@example.com", 
                "username": "jane_smith",
                "password": "password123",
                "shipping_address": "789 Pine Rd, Village, State 11223",
                "balance": Decimal("2500.00")
            },
            {
                "email": "bob@example.com",
                "username": "bob_wilson", 
                "password": "password123",
                "shipping_address": "321 Elm St, City, State 44556",
                "balance": Decimal("750.00")
            }
        ]
        
        created_users = []
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                password=get_password_hash(user_data["password"]),
                shipping_address=user_data["shipping_address"],
                is_admin=False,
                status="active"
            )
            db.add(user)
            db.flush()
            
            account = Account(
                user_id=user.id,
                balance=user_data["balance"]
            )
            db.add(account)
            created_users.append(user)
        
        # Create sample products
        print("📦 Creating sample products...")
        products_data = [
            {
                "name": "Vintage Leather Jacket",
                "description": "Genuine vintage leather jacket from the 1980s in excellent condition",
                "price": Decimal("299.99"),
                "stock_quantity": 5,
                "image_url": "https://example.com/images/leather-jacket.jpg"
            },
            {
                "name": "Antique Pocket Watch",
                "description": "Beautiful gold-plated pocket watch from 1920s, fully functional",
                "price": Decimal("450.00"),
                "stock_quantity": 2,
                "image_url": "https://example.com/images/pocket-watch.jpg"
            },
            {
                "name": "Retro Denim Jeans",
                "description": "Classic 1970s denim jeans with original vintage wash",
                "price": Decimal("89.99"),
                "stock_quantity": 10,
                "image_url": "https://example.com/images/denim-jeans.jpg"
            },
            {
                "name": "Vintage Sunglasses",
                "description": "Retro-style sunglasses with original case, perfect condition",
                "price": Decimal("125.50"),
                "stock_quantity": 8,
                "image_url": "https://example.com/images/sunglasses.jpg"
            },
            {
                "name": "Classic Vinyl Record",
                "description": "Rare vintage vinyl record from 1960s, includes original sleeve",
                "price": Decimal("75.00"),
                "stock_quantity": 15,
                "image_url": "https://example.com/images/vinyl-record.jpg"
            },
            {
                "name": "Antique Brass Lamp",
                "description": "Ornate brass table lamp from Victorian era, fully restored",
                "price": Decimal("320.00"),
                "stock_quantity": 3,
                "image_url": "https://example.com/images/brass-lamp.jpg"
            }
        ]
        
        created_products = []
        for product_data in products_data:
            product = Product(**product_data)
            db.add(product)
            db.flush()
            created_products.append(product)
        
        # Create sample cart items
        print("🛒 Creating sample cart items...")
        for i, user in enumerate(created_users[:2]):  # Add cart items for first 2 users
            for j, product in enumerate(created_products[:2]):  # Add 2 products each
                cart_item = Cart(
                    user_id=user.id,
                    product_id=product.id,
                    quantity=1 if i == 0 else 2  # Vary quantities
                )
                db.add(cart_item)
        
        # Create sample orders
        print("📋 Creating sample orders...")
        orders_data = [
            {
                "user": created_users[0],
                "product": created_products[0],
                "quantity": 1,
                "amount": created_products[0].price,
                "unit_price": created_products[0].price,
                "order_status": "completed",
                "shipping_address": created_users[0].shipping_address
            },
            {
                "user": created_users[1],
                "product": created_products[1],
                "quantity": 1,
                "amount": created_products[1].price,
                "unit_price": created_products[1].price,
                "order_status": "pending",
                "shipping_address": created_users[1].shipping_address
            }
        ]
        
        created_orders = []
        for order_data in orders_data:
            order = Order(
                product_id=order_data["product"].id,
                user_id=order_data["user"].id,
                amount=order_data["amount"],
                quantity=order_data["quantity"],
                unit_price=order_data["unit_price"],
                order_status=order_data["order_status"],
                shipping_address=order_data["shipping_address"]
            )
            db.add(order)
            db.flush()
            created_orders.append(order)
            
            # Create transaction for completed order
            if order_data["order_status"] == "completed":
                transaction = Transaction(
                    order_id=order.id,
                    reference=f"PAY_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    status="success",
                    amount=order_data["amount"],
                    currency="NGN",
                    channel="card",
                    paid_at=datetime.now()
                )
                db.add(transaction)
        
        # Create sample guest sessions
        print("👤 Creating sample guest sessions...")
        for i in range(3):
            guest = Guest()
            db.add(guest)
        
        # Commit all changes
        db.commit()
        
        print("✅ Database seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"   Users: {len(created_users) + 1} (including admin)")
        print(f"   Products: {len(created_products)}")
        print(f"   Cart items: 4")
        print(f"   Orders: {len(created_orders)}")
        print(f"   Transactions: 1")
        print(f"   Guest sessions: 3")
        
        print("\n🔑 Login credentials:")
        print("   Admin: admin@vintique.com / admin123")
        print("   User 1: john@example.com / password123")
        print("   User 2: jane@example.com / password123")
        print("   User 3: bob@example.com / password123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
