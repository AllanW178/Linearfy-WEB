
# Those Python library build-in modules are useful for Linearfy, that's why we are using them.
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import re
import os


app = Flask(__name__)



# We need to load all the essential database requirements that we need to make Linearfy work.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

db_path = os.path.join(BASE_DIR, 'linearfy.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SECRET_KEY'] = 'linearfy_secret_key_12345'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False) # NEW for Admin panel

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_new = db.Column(db.Boolean, default=False)
    is_sale = db.Column(db.Boolean, default=False)


# For Sprint #2 improvements - New Database Tables:

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')





with app.app_context():
    db.create_all()

    if Product.query.count() == 0:
        sample_products = [

            Product(
                name="Matte Black Pen",
                price=18.00,
                category="stationery",
                image="matte-black-pen.jpg",
                description="A sleek matte black pen designed for smooth writing and a premium minimalist feel."
            ),

            Product(
                name="Woven Throw Blanket",
                price=65.00,
                category="home",
                image="woven-throw-blanket.jpg",
                description="Soft woven cotton throw blanket perfect for adding warmth and comfort to your home.",
                is_sale=True
            ),

            Product(
                name="Concrete Bookends",
                price=42.00,
                category="home",
                image="concrete-bookends.jpg",
                description="Modern sculptural bookends crafted with a minimalist aesthetic for stylish organisation."
            ),

            Product(
                name="Linear Desk Lamp",
                price=89.00,
                category="lighting",
                image="desk-lamp.jpg",
                description="An adjustable desk lamp with clean lines, ideal for focused work and elegant spaces.",
                is_new=True
            ),

            Product(
                name="Ceramic Mug Set",
                price=35.00,
                category="home",
                image="ceramic-mug.jpg",
                description="Minimalist ceramic mugs designed for everyday coffee and tea moments."
            ),

            Product(
                name="Minimalist Planner",
                price=24.00,
                category="stationery",
                image="planner.jpg",
                description="Stay organised with a beautifully designed planner focused on simplicity and productivity."
            ),

            Product(
                name="Pendant Light",
                price=110.00,
                category="lighting",
                image="pendant-light.jpg",
                description="Elegant pendant lighting that blends modern design with functional illumination."
            ),

            Product(
                name="Leather Notebook",
                price=32.00,
                category="stationery",
                image="leather-notebook.jpg",
                description="Premium leather notebook with durable pages for journaling, planning, and ideas."
            )

        ]

        db.session.bulk_save_objects(sample_products)
        db.session.commit()



@app.route('/')
def home():

    page = request.args.get(
        'page',
        1,
        type=int
    )

    featured_query = Product.query.filter(
        (Product.is_new == True) |
        (Product.is_sale == True) |
        (Product.id <= 5)
    ).order_by(Product.id.desc())

    pagination = featured_query.paginate(
        page=page,
        per_page=5,
        error_out=False
    )

    products = pagination.items

    return render_template(
        'index.html',
        products=products,
        pagination=pagination
    )


@app.route('/shop')
def shop():

    category = request.args.get('category', 'all')
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)

    query = Product.query



    if category != 'all':

        if category == 'home':
            query = query.filter(
                Product.category == 'home'
            )

        elif category == 'lighting':
            query = query.filter(
                Product.category == 'lighting'
            )

        elif category == 'stationery':
            query = query.filter(
                Product.category == 'stationery'
            )



    if sort == 'price-low':
        query = query.order_by(Product.price.asc())

    elif sort == 'price-high':
        query = query.order_by(Product.price.desc())

    else:
        query = query.order_by(Product.id.desc())



    per_page = 4

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    products = pagination.items

    return render_template(
        'shop.html',
        products=products,
        pagination=pagination,
        current_category=category,
        current_sort=sort
    )

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    return render_template(
        'product.html',
        product=product
    )


@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):



    if 'user_id' not in session:

        flash(
            'Please log in before placing an order.'
        )

        return redirect(
            url_for('register')
        )

    product = Product.query.get_or_404(
        product_id
    )

    cart = session.get(
        'cart',
        {}
    )

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session['cart'] = cart

    flash(
        f'Successfully added {product.name} to cart.'
    )

    return redirect(
        url_for('cart')
    )


@app.route('/cart')
def cart():

    cart_items = []
    total = 0

    cart = session.get('cart', {})

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:
            item_total = product.price * quantity
            total += item_total

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })

    return render_template(
        'cart.html',
        cart_items=cart_items,
        total=total
    )


@app.route('/update-cart/<int:product_id>/<action>')
def update_cart(product_id, action):

    cart = session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:

        if action == 'increase':
            cart[product_id] += 1

            product = Product.query.get(int(product_id))

            flash(f'Increased quantity of {product.name}.')

        elif action == 'decrease':

            product = Product.query.get(int(product_id))

            cart[product_id] -= 1

            flash(f'Decreased quantity of {product.name}.')

            if cart[product_id] <= 0:
                del cart[product_id]

        elif action == 'remove':

            product = Product.query.get(int(product_id))

            del cart[product_id]

            flash(f'{product.name} removed from cart.')

    session['cart'] = cart

    return redirect(url_for('cart'))


@app.route('/checkout-simulate')
def checkout_simulate():
    if 'user_id' not in session:
        flash('Please log in before checking out.')
        return redirect(url_for('register'))

    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.')
        return redirect(url_for('shop'))

    total = 0
    order_items = []
    
    # Calculate totals and build the OrderItems
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            total += item_total
            order_item = OrderItem(
                product_id=product.id, 
                quantity=quantity, 
                price_at_purchase=product.price
            )
            order_items.append(order_item)

    # Create the Order and attach the items
    new_order = Order(user_id=session['user_id'], total_price=total)
    new_order.items = order_items
    
    db.session.add(new_order)
    db.session.commit()

    # Clear the temporary cart now that it is permanently saved
    session.pop('cart', None)
    flash('Purchase successful! Your order has been saved to your account history.')
    
    return redirect(url_for('account'))

@app.route('/account')
def account():
    
    if 'user_id' not in session:
        flash('Please log in to view your account.')
        return redirect(url_for('register'))
    

    user = User.query.get(session['user_id'])
    
    
    if user is None:
        session.clear()
        flash('Session expired or invalid. Please log in again.')
        return redirect(url_for('register'))

    
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.order_date.desc()).all()
    
    return render_template('account.html', user=user, orders=orders)


@app.route('/edit-account', methods=['GET', 'POST'])
def edit_account():

    if 'user_id' not in session:
        flash('Please log in to edit your details.')
        return redirect(url_for('register'))
        
    user = User.query.get(session['user_id'])
    if user is None:
        session.clear()
        return redirect(url_for('register'))

    if request.method == 'POST':
        new_email = request.form.get('email')
        new_password = request.form.get('new_password')
        
        
        if new_email != user.email:
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user:
                flash('That email is already registered to another account.')
                return redirect(url_for('edit_account'))
                

        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = new_email
        user.dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date()
        
        
        if new_password:
            password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$'
            if not re.match(password_regex, new_password):
                flash('New password must be at least 8 characters and contain letters and numbers.')
                return redirect(url_for('edit_account'))
            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            
        db.session.commit()
        
        
        session['user_name'] = user.first_name 
        
        flash('Your account details have been successfully updated.')
        return redirect(url_for('account'))

    return render_template('edit_account.html', user=user)





@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob_str = request.form.get('dob')
        email = request.form.get('email')
        password = request.form.get('password')



        password_regex = (
            r'^(?=.*[A-Za-z])'
            r'(?=.*\d)'
            r'[A-Za-z\d@$!%*#?&]{8,}$'
        )

        if not re.match(
            password_regex,
            password
        ):

            flash(
                'Password must be at least 8 characters and contain letters and numbers.'
            )

            return redirect(
                url_for('register')
            )



        email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

        if not re.match(email_regex, email):
            flash('Please enter a valid email address.')

            return redirect(url_for('register'))


        existing_user = User.query.filter_by(
            email=email

        ).first()

        if existing_user:
            flash('Email already exists.')
            return redirect(url_for('register'))

        dob = datetime.strptime(
            dob_str,
            '%Y-%m-%d'
        ).date()

        today = datetime.today().date()

        age = today.year - dob.year - (
            (today.month, today.day)
            <
            (dob.month, dob.day)
        )

        if age < 16 or age > 25:
            flash(
                'You must be between 18 and 25 years old to register.'
            )

            return redirect(
                url_for('register')
            )

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode('utf-8')

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['user_name'] = new_user.first_name
        session['is_admin'] = new_user.is_admin

        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():

    email = request.form.get('login_email')
    password = request.form.get('login_password')

    user = User.query.filter_by(
        email=email
    ).first()

    if user and bcrypt.check_password_hash(
        user.password,
        password
    ):
        session['user_id'] = user.id
        session['user_name'] = user.first_name
        session['is_admin'] = user.is_admin

        return redirect(url_for('home'))

    flash('Invalid email or password.')

    return redirect(url_for('register'))


@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('home'))



@app.route('/make-me-admin')
def make_me_admin():

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            user.is_admin = True
            db.session.commit()
            session['is_admin'] = True
            flash('Success! You are now an Administrator.')
    return redirect(url_for('account'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if not session.get('is_admin'):
        flash('Access denied. Administrators only.')
        return redirect(url_for('home'))


    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        image = request.form.get('image')
        description = request.form.get('description')
        is_new = 'is_new' in request.form
        is_sale = 'is_sale' in request.form

        new_product = Product(
            name=name, price=price, category=category, 
            image=image, description=description, 
            is_new=is_new, is_sale=is_sale
        )
        db.session.add(new_product)
        db.session.commit()
        
        flash(f'Product "{name}" was added to the store.')
        return redirect(url_for('admin'))


    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin.html', products=products)

@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
    # DELETE functionality
    if not session.get('is_admin'):
        return redirect(url_for('home'))
        
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    flash(f'Product "{product.name}" has been permanently deleted.')
    return redirect(url_for('admin'))



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404










if __name__ == '__main__':
    app.run(debug=True)


