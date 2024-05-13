from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/shop"
mongo = PyMongo(app)

@app.route('/')
def index():
    products = mongo.db.products.find()
    return render_template('index.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        colour = request.form['colour']
        brand = request.form['brand']
        price = request.form['price']
        image_url = request.form['image_url']
        product_id = request.form['product_id']
        
        mongo.db.products.insert_one({
            "_id": product_id,
            "name": name,
            "colour": colour,
            "brand": brand,
            "price": price,
            "image_url": image_url
        })
        
        return redirect(url_for('index'))
    
    return render_template('add_product.html')



@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_id = request.form['product_id']
    print("Deleting product:", product_id)  
    mongo.db.products.delete_one({'_id': product_id})
    return redirect(url_for('index'))

@app.route('/update_product', methods=['POST'])
def update_product():
    if request.method == 'POST':
        product_id = request.form['product_id']

        product_details = mongo.db.products.find_one({'_id': product_id})

        return render_template('update_form.html', product=product_details)
    else:
        return "Method not allowed"

@app.route('/update_product_submit', methods=['POST'])
def update_product_submit():
    if request.method == 'POST':
        product_id = request.form['product_id']
        name = request.form['name']
        colour = request.form['colour']
        brand = request.form['brand']
        price = request.form['price']
        image_url = request.form['image_url']
        
        
        mongo.db.products.update_one(
            {'_id': product_id},
            {'$set': {
                'name': name,
                'colour': colour,
                'brand': brand,
                'price': price,
                'image_url': image_url
            }}
        )
        
        return redirect(url_for('index'))
    else:
        return "Method not allowed"
    
@app.route('/update_product_page')
def update_product_page():
    return render_template('update_product.html')

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']
    products = mongo.db.products.find({"name": {"$regex": search_query, "$options": "i"}})
    return render_template('search_results.html', products=products)

@app.route('/filter_by_colour', methods=['POST'])
def filter_by_colour():
    selected_color = request.form.get('color')
    filtered_products = []
    for product in mongo.db.products.find():
        if selected_color.lower() in product['colour'].lower():
            filtered_products.append(product)
    return render_template('filter_by_colour.html', filtered_products=filtered_products)

@app.route('/summary')
def summary():
    pipeline = [
        {"$group": {"_id": "$name", "count": {"$sum": 1}}}
    ]
    result = mongo.db.products.aggregate(pipeline)
    category_counts = {category['_id']: category['count'] for category in result}
    
    total_products = sum(category_counts.values())
    
    return render_template('summary.html', category_counts=category_counts, total_products=total_products)

if __name__ == '__main__':
    app.run(debug=True)
