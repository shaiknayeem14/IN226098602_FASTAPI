from fastapi import FastAPI
app = FastAPI()
# ── Temporary database ──────────
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook','price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub','price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set','price':  49, 'category': 'Stationery',  'in_stock': True },
    {'id': 5, 'name': 'Laptop Stand','price':  1299, 'category': 'Electronics',  'in_stock': True },
    {'id': 6, 'name': 'Mechanical Keyboard','price':  2499, 'category': 'Electronics',  'in_stock': True },
    {'id': 7, 'name': 'Webcam','price':  1899, 'category': 'Electronics',  'in_stock': False },
]
# ── Endpoint 1 — Return all products ──────────────────────────
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}
# ── Endpoint 2 — Return all category ──────────────────────────
@app.get('/products/category/{category_name}')
def get_by_category(category_name:str):
    result=[p for p in products if p["category"]==category_name]
    if not result:
        return {'error': 'No Products not found in this category'}
    return {'category':category_name,'products':result,'total':len(result)}
# ── Endpoint 3 — Return all instock ──────────────────────────
@app.get('/products/instock')
def get_instock_products():
    instock=[p for p in products if p["in_stock"]==True]
    return {'in_stock_products':instock,'count':len(instock)}
# ── Endpoint 4 — Return store summary ──────────────────────────
@app.get('/store/summary')
def store_summary():
    count=len([p for p in products if p["in_stock"]])
    out_stock=len(products)-count
    categories=list(set([p["category"] for p in products]))
    return {"store_name":"My E-commerce Store","total_products":len(products),"in_stock":count,"out_of_stock":out_stock,"categories":categories}
# ── Endpoint 5 — Return for search ──────────────────────────
@app.get('/products/search/{keyword}')
def search_products(keyword: str):
    m=[p for p in products if keyword.lower() in p["name"].lower()]
    if not m:
        return {"message":"No products matched your search"}
    return {"matched_products":m,"total_matches":len(m)}
# ── Endpoint 6 — Bonus ──────────────────────────
@app.get('/products/deals')
def get_deals():
    c=min(products,key=lambda p:p["price"])
    expensive=max(products,key=lambda p:p["price"])
    return {"best_deal":c,"premium_pick":expensive}