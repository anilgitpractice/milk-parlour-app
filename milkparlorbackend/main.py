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


class OrderCreate(BaseModel):
    customer_name: str
    item: str
    status: str = "Pending"


class OrderUpdate(BaseModel):
    status: str


class UserCreate(BaseModel):
    name: str
    phone: str
    password: str


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
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
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

    # Calculate a simple estimated revenue based on Delivered orders (e.g., $50 per delivered order for now)
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
    
    # Update their status with the dates!
    customer.status = f"Paused: {req.start_date} to {req.end_date}"
    db.commit()
    return {"message": "Subscription paused successfully"}

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
    # Create a new database record
    db_customer = models.Customer(
        name=customer.name,
        phone=customer.phone,
        subscription=customer.subscription,
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.post("/api/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if phone number already exists
    existing_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # 2. Hash the password and save the user for login
    hashed_pwd = pwd_context.hash(user.password)
    db_user = models.User(name=user.name, phone=user.phone, hashed_password=hashed_pwd)
    db.add(db_user)
    
    # 3. MAGIC: Automatically add them to the Admin Dashboard Customers list!
    existing_customer = db.query(models.Customer).filter(models.Customer.phone == user.phone).first()
    if not existing_customer:
        db_customer = models.Customer(
            name=user.name, 
            phone=user.phone, 
            subscription="Needs Setup", # Default text until they buy something
            status="Active"
        )
        db.add(db_customer)
        
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully", "user_name": db_user.name, "phone": db_user.phone}


@app.post("/api/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find the user by phone number
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid phone number or password")

    # Verify the password
    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid phone number or password")

    return {"message": "Login successful", "user_name": db_user.name, "phone": db_user.phone}

