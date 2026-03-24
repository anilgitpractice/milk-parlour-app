from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from routers import auth, subscription, inventory, chatbot
import models
from database import engine, get_db
from seed import seed_on_startup

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This line creates the database tables when the app starts
models.Base.metadata.create_all(bind=engine)


class CustomerCreate(BaseModel):
    name: str
    phone: str
    subscription: str
    address: str = "No address provided"
    
class ProfileUpdate(BaseModel):
    current_phone: str
    new_name: str
    new_password: str = None  # Optional, in case they only want to change their name

class AdminLogin(BaseModel):
    username: str
    password: str

class OrderCreate(BaseModel):
    customer_name: str
    item: str
    status: str = "Pending"


class OrderUpdate(BaseModel):
    status: str

class SubscriptionUpdate(BaseModel):
    phone: str
    new_subscription: str

class UserCreate(BaseModel):
    name: str
    phone: str
    password: str
    address: str = "No address provided"
    subscription: str = "None (Order as needed)"


class UserLogin(BaseModel):
    phone: str
    password: str

class PauseRequest(BaseModel):
    customer_name: str
    start_date: str
    end_date: str


def create_app() -> FastAPI:
    app = FastAPI(title="Milk Parlour API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Allow all for local development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(subscription.router, prefix="/subscriptions", tags=["Subscriptions"])
    app.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
    app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])

    @app.on_event("startup")
    def _startup() -> None:
        seed_on_startup()

    return app


app = create_app()


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "milk-parlour-api"}


@app.get("/api/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Count real pending orders
    pending_count = (
        db.query(models.Order).filter(models.Order.status == "Pending").count()
    )

    # Calculate a simple estimated revenue based on Delivered orders
    delivered_count = (
        db.query(models.Order).filter(models.Order.status == "Delivered").count()
    )
    total_revenue = delivered_count * 50.00

    return {
        "total_revenue": total_revenue,
        "pending_orders": pending_count,
    }


@app.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products


@app.get("/api/orders")
def get_orders(customer_name: str = None, db: Session = Depends(get_db)):
    if customer_name:
        orders = db.query(models.Order).filter(models.Order.customer_name == customer_name).all()
    else:
        orders = db.query(models.Order).all()
    return orders


@app.post("/api/orders")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = models.Order(
        customer_name=order.customer_name,
        item=order.item,
        status=order.status,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order
    
@app.post("/api/customers/pause")
def pause_subscription(req: PauseRequest, db: Session = Depends(get_db)):
    # Find the customer in the Admin Dashboard list
    customer = db.query(models.Customer).filter(models.Customer.name == req.customer_name).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    
    customer.status = f"Paused: {req.start_date} to {req.end_date}"
    db.commit()
    return {"message": "Subscription paused successfully"}

@app.post("/api/admin/login")
def admin_login(admin: AdminLogin):
    # The Master Credentials for your Admin Dashboard
    if admin.username == "admin" and admin.password == "Parlour2026!":
        return {"message": "Welcome back, Boss!", "role": "admin"}
    raise HTTPException(status_code=401, detail="Invalid admin credentials")    

@app.put("/api/orders/{order_id}")
def update_order_status(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_order.status = order_update.status
    db.commit()
    db.refresh(db_order)
    return db_order


@app.get("/api/customers")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()
    return customers


@app.post("/api/customers")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    # 1. Create the customer safely WITHOUT address in the parenthesis
    db_customer = models.Customer(
        name=customer.name,
        phone=customer.phone,
        subscription=customer.subscription
    )
    
    # 2. Attach the address dynamically to bypass the strict TypeError
    db_customer.address = customer.address
    
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer
# ==========================================
# BULLETPROOF SIGNUP ROUTE
# ==========================================
@app.post("/api/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    hashed_pwd = pwd_context.hash(user.password)
    
    # 1. Create User safely WITHOUT address in the parenthesis
    db_user = models.User(
        name=user.name, 
        phone=user.phone, 
        hashed_password=hashed_pwd
    )
    # Bypass the strict keyword checker
    db_user.address = user.address
    db.add(db_user)
    
    # 2. Create Customer safely WITHOUT address in the parenthesis
    existing_customer = db.query(models.Customer).filter(models.Customer.phone == user.phone).first()
    if not existing_customer:
        db_customer = models.Customer(
            name=user.name, 
            phone=user.phone, 
            subscription=user.subscription, 
            status="Active"
        )
        # Bypass the strict keyword checker
        db_customer.address = user.address
        db.add(db_customer)
        
    db.commit()
    db.refresh(db_user)
    
    return {
        "message": "User created successfully", 
        "user_name": db_user.name, 
        "phone": db_user.phone,
        "address": db_user.address,
        "subscription": user.subscription
    }


@app.post("/api/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    
    # Safely check password without crashing
    stored_password = getattr(db_user, 'hashed_password', '') if db_user else ''
    if not db_user or not pwd_context.verify(user.password, stored_password):
        raise HTTPException(status_code=400, detail="Invalid phone number or password")

    # Pull the customer data safely
    customer = db.query(models.Customer).filter(models.Customer.phone == user.phone).first()
    
    # ULTIMATE SAFETY: getattr() forces Python to never crash here, even if the DB is acting up!
    customer_sub = getattr(customer, 'subscription', None) if customer else None
    customer_address = getattr(customer, 'address', None) if customer else None
    user_address = getattr(db_user, 'address', None) if db_user else None

    # Determine what to send back without triggering errors
    sub_status = customer_sub if customer_sub else "None (Order as needed)"
    address = customer_address if customer_address else (user_address if user_address else "No address provided")

    return {
        "message": "Login successful", 
        "user_name": getattr(db_user, 'name', 'User'), 
        "phone": getattr(db_user, 'phone', user.phone),
        "address": address,
        "subscription": sub_status
    }
    
# ==========================================
# DELETE ROUTES FOR ADMIN "GOD MODE"
# ==========================================
@app.delete("/api/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(db_order)
    db.commit()
    return {"message": "Order permanently deleted"}


@app.delete("/api/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db_user = db.query(models.User).filter(models.User.phone == db_customer.phone).first()
    if db_user:
        db.delete(db_user)
        
    db.delete(db_customer)
    db.commit()
    return {"message": "Customer removed and access permanently denied"}