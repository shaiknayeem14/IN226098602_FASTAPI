from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# ------------------ DATA ------------------

cars = [
    {"id": 1, "model": "Swift", "brand": "Maruti", "type": "Hatchback", "price_per_day": 1200, "fuel_type": "Petrol", "is_available": True},
    {"id": 2, "model": "City", "brand": "Honda", "type": "Sedan", "price_per_day": 2500, "fuel_type": "Petrol", "is_available": True},
    {"id": 3, "model": "Creta", "brand": "Hyundai", "type": "SUV", "price_per_day": 3000, "fuel_type": "Diesel", "is_available": True},
    {"id": 4, "model": "Fortuner", "brand": "Toyota", "type": "SUV", "price_per_day": 5000, "fuel_type": "Diesel", "is_available": True},
    {"id": 5, "model": "Nexon EV", "brand": "Tata", "type": "SUV", "price_per_day": 3500, "fuel_type": "Electric", "is_available": True},
    {"id": 6, "model": "BMW X5", "brand": "BMW", "type": "Luxury", "price_per_day": 9000, "fuel_type": "Petrol", "is_available": True},
]

rentals = []
rental_counter = 1


# ------------------ MODELS ------------------

class RentalRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    car_id: int = Field(..., gt=0)
    days: int = Field(..., gt=0, le=30)
    license_number: str = Field(..., min_length=8)
    insurance: bool = False
    driver_required: bool = False


class NewCar(BaseModel):
    model: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    type: str = Field(..., min_length=2)
    price_per_day: int = Field(..., gt=0)
    fuel_type: str = Field(..., min_length=2)
    is_available: bool = True


# ------------------ HELPERS ------------------

def find_car(car_id):
    for car in cars:
        if car["id"] == car_id:
            return car
    return None


def calculate_rental_cost(price, days, insurance, driver):
    base = price * days

    discount = 0
    if days >= 15:
        discount = base * 0.25
    elif days >= 7:
        discount = base * 0.15

    insurance_cost = 500 * days if insurance else 0
    driver_cost = 800 * days if driver else 0

    total = base - discount + insurance_cost + driver_cost

    return {
        "base_cost": base,
        "discount": discount,
        "insurance_cost": insurance_cost,
        "driver_cost": driver_cost,
        "total_cost": total
    }


def filter_cars_logic(type, brand, fuel_type, max_price, is_available):
    result = cars

    if type is not None:
        result = [c for c in result if c["type"].lower() == type.lower()]
    if brand is not None:
        result = [c for c in result if c["brand"].lower() == brand.lower()]
    if fuel_type is not None:
        result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]
    if max_price is not None:
        result = [c for c in result if c["price_per_day"] <= max_price]
    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]

    return result


# ------------------ DAY 1 ------------------

@app.get("/")
def home():
    return {"message": "Welcome to SpeedRide Car Rentals"}


@app.get("/cars")
def get_cars():
    return {
        "cars": cars,
        "total": len(cars),
        "available_count": len([c for c in cars if c["is_available"]])
    }


@app.get("/cars/summary")
def summary():
    types = {}
    fuels = {}

    for c in cars:
        types[c["type"]] = types.get(c["type"], 0) + 1
        fuels[c["fuel_type"]] = fuels.get(c["fuel_type"], 0) + 1

    cheapest = min(cars, key=lambda x: x["price_per_day"])
    expensive = max(cars, key=lambda x: x["price_per_day"])

    return {
        "total": len(cars),
        "available": len([c for c in cars if c["is_available"]]),
        "by_type": types,
        "by_fuel": fuels,
        "cheapest": cheapest,
        "most_expensive": expensive
    }


@app.get("/cars/{car_id}")
def get_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@app.get("/rentals")
def get_rentals():
    return {"rentals": rentals, "total": len(rentals)}


# ------------------ DAY 2 & 3 ------------------

@app.post("/rentals", status_code=201)
def create_rental(req: RentalRequest):
    global rental_counter

    car = find_car(req.car_id)
    if not car or not car["is_available"]:
        raise HTTPException(status_code=400, detail="Car not available")

    cost = calculate_rental_cost(car["price_per_day"], req.days, req.insurance, req.driver_required)

    car["is_available"] = False

    rental = {
        "rental_id": rental_counter,
        "customer_name": req.customer_name,
        "car_id": req.car_id,
        "car_model": car["model"],
        "car_brand": car["brand"],
        "days": req.days,
        "insurance": req.insurance,
        "driver_required": req.driver_required,
        "status": "active",
        **cost
    }

    rentals.append(rental)
    rental_counter += 1

    return rental


@app.get("/cars/filter")
def filter_cars(
        type: Optional[str] = None,
        brand: Optional[str] = None,
        fuel_type: Optional[str] = None,
        max_price: Optional[int] = None,
        is_available: Optional[bool] = None
):
    return filter_cars_logic(type, brand, fuel_type, max_price, is_available)


# ------------------ DAY 4 ------------------

@app.post("/cars", status_code=201)
def add_car(new_car: NewCar):
    for c in cars:
        if c["model"] == new_car.model and c["brand"] == new_car.brand:
            raise HTTPException(status_code=400, detail="Car already exists")

    car = new_car.dict()
    car["id"] = len(cars) + 1
    cars.append(car)
    return car


@app.put("/cars/{car_id}")
def update_car(car_id: int,
               price_per_day: Optional[int] = None,
               is_available: Optional[bool] = None):
    car = find_car(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    if price_per_day is not None:
        car["price_per_day"] = price_per_day
    if is_available is not None:
        car["is_available"] = is_available

    return car


@app.delete("/cars/{car_id}")
def delete_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    for r in rentals:
        if r["car_id"] == car_id and r["status"] == "active":
            raise HTTPException(status_code=400, detail="Car has active rental")

    cars.remove(car)
    return {"message": "Car deleted"}


# ------------------ DAY 5 ------------------

@app.get("/rentals/{rental_id}")
def get_rental(rental_id: int):
    for r in rentals:
        if r["rental_id"] == rental_id:
            return r
    raise HTTPException(status_code=404, detail="Rental not found")


@app.post("/return/{rental_id}")
def return_car(rental_id: int):
    rental = None
    for r in rentals:
        if r["rental_id"] == rental_id:
            rental = r

    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    rental["status"] = "returned"

    car = find_car(rental["car_id"])
    car["is_available"] = True

    return rental


@app.get("/rentals/active")
def active_rentals():
    return [r for r in rentals if r["status"] == "active"]


@app.get("/rentals/by-car/{car_id}")
def rentals_by_car(car_id: int):
    return [r for r in rentals if r["car_id"] == car_id]


@app.get("/cars/unavailable")
def unavailable():
    return [c for c in cars if not c["is_available"]]


# ------------------ DAY 6 ------------------

@app.get("/cars/search")
def search(keyword: str):
    result = [
        c for c in cars
        if keyword.lower() in c["model"].lower()
        or keyword.lower() in c["brand"].lower()
        or keyword.lower() in c["type"].lower()
    ]
    return {"results": result, "total_found": len(result)}


@app.get("/cars/sort")
def sort(sort_by: str = "price_per_day"):
    if sort_by not in ["price_per_day", "brand", "type"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    return sorted(cars, key=lambda x: x[sort_by])


@app.get("/cars/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit

    total = len(cars)
    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "total_pages": total_pages,
        "data": cars[start:end]
    }


@app.get("/rentals/search")
def rental_search(name: str):
    return [r for r in rentals if name.lower() in r["customer_name"].lower()]


@app.get("/rentals/sort")
def rental_sort(sort_by: str = "total_cost"):
    return sorted(rentals, key=lambda x: x.get(sort_by, 0))


@app.get("/rentals/page")
def rental_page(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    return rentals[start:end]


@app.get("/cars/browse")
def browse(
        keyword: Optional[str] = None,
        type: Optional[str] = None,
        fuel_type: Optional[str] = None,
        max_price: Optional[int] = None,
        is_available: Optional[bool] = None,
        sort_by: str = "price_per_day",
        order: str = "asc",
        page: int = 1,
        limit: int = 3
):
    result = cars

    if keyword:
        result = [c for c in result if keyword.lower() in c["model"].lower()]

    result = filter_cars_logic(type, None, fuel_type, max_price, is_available)

    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": len(result),
        "page": page,
        "results": result[start:end]
    }