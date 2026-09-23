from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import text
from datetime import datetime
from functools import wraps
from uuid import uuid4
from werkzeug.utils import secure_filename
import os
import re


app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(BASE_DIR, 'linearfy.db')}"
)
app.config["SECRET_KEY"] = os.environ.get(
    "LINEARFY_SECRET_KEY",
    "development-only-change-me",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

ALLOWED_CATEGORIES = {"home", "lighting", "stationery"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

MAX_LISTINGS_PER_DAY = 5
MAX_STOCK_PER_LISTING = 999
MAX_PRICE_PER_LISTING = 10000

# Assessment-only administrator account.
DEMO_ADMIN_EMAIL = "admin@linearfy.test"
DEMO_ADMIN_PASSWORD = "iamreallycookedonthis1"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_new = db.Column(db.Boolean, default=False)
    is_sale = db.Column(db.Boolean, default=False)

    stock_count = db.Column(db.Integer, nullable=False, default=10)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="approved")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    seller = db.relationship(
        "User",
        backref=db.backref("listings", lazy=True),
    )


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan",
    )


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

    product = db.relationship("Product")


class ProductReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    reason = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    product = db.relationship("Product")
    reporter = db.relationship("User", foreign_keys=[reporter_id])


class WishlistItem(db.Model):
    __tablename__ = "wishlist_item"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    product = db.relationship("Product")

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_wishlist_user_product",
        ),
    )


def add_missing_user_columns():
    """Adds fields missing from older versions of the User table."""
    with db.engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(user)"))
        }

        if "created_at" not in columns:
            connection.execute(
                text("ALTER TABLE user ADD COLUMN created_at DATETIME")
            )


def add_missing_product_columns():
    """Adds fields missing from older versions of the Product table."""
    with db.engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(product)"))
        }

        additions = {
            "stock_count": "INTEGER NOT NULL DEFAULT 10",
            "seller_id": "INTEGER",
            "status": "VARCHAR(20) NOT NULL DEFAULT 'approved'",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        }

        for column, definition in additions.items():
            if column not in columns:
                connection.execute(
                    text(f"ALTER TABLE product ADD COLUMN {column} {definition}")
                )

        connection.execute(
            text(
                "UPDATE product "
                "SET status = COALESCE(status, 'approved'), "
                "created_at = COALESCE(created_at, CURRENT_TIMESTAMP), "
                "updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)"
            )
        )


def add_missing_product_report_columns():
    """Adds the report status field if an older report table already exists."""
    with db.engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.execute(
                text("PRAGMA table_info(product_report)")
            )
        }

        if "status" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE product_report "
                    "ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending'"
                )
            )


def create_demo_admin():
    """Creates/resets an assessment-only administrator account."""
    admin = User.query.filter_by(email=DEMO_ADMIN_EMAIL).first()

    password_hash = bcrypt.generate_password_hash(
        DEMO_ADMIN_PASSWORD
    ).decode("utf-8")

    if admin is None:
        admin = User(
            first_name="Demo",
            last_name="Administrator",
            dob=datetime(2000, 1, 1).date(),
            email=DEMO_ADMIN_EMAIL,
            password=password_hash,
            is_admin=True,
        )
        db.session.add(admin)
    else:
        admin.password = password_hash
        admin.is_admin = True

    db.session.commit()


def create_sample_products():
    if Product.query.count() > 0:
        return

    products = [
        Product(
            name="Matte Black Pen",
            price=18,
            category="stationery",
            image="matte-black-pen.jpg",
            description=(
                "A sleek matte black pen designed for smooth writing "
                "and a premium minimalist feel."
            ),
            stock_count=18,
        ),
        Product(
            name="Woven Throw Blanket",
            price=65,
            category="home",
            image="woven-throw-blanket.jpg",
            description=(
                "Soft woven cotton throw blanket perfect for adding "
                "warmth and comfort to your home."
            ),
            stock_count=7,
            is_sale=True,
        ),
        Product(
            name="Concrete Bookends",
            price=42,
            category="home",
            image="concrete-bookends.jpg",
            description=(
                "Modern sculptural bookends crafted with a minimalist "
                "aesthetic for stylish organisation."
            ),
            stock_count=4,
        ),
        Product(
            name="Linear Desk Lamp",
            price=89,
            category="lighting",
            image="desk-lamp.jpg",
            description=(
                "An adjustable desk lamp with clean lines, ideal for "
                "focused work and elegant spaces."
            ),
            stock_count=10,
            is_new=True,
        ),
        Product(
            name="Ceramic Mug Set",
            price=35,
            category="home",
            image="ceramic-mug.jpg",
            description=(
                "Minimalist ceramic mugs designed for everyday coffee "
                "and tea moments."
            ),
            stock_count=12,
        ),
        Product(
            name="Minimalist Planner",
            price=24,
            category="stationery",
            image="planner.jpg",
            description=(
                "Stay organised with a beautifully designed planner "
                "focused on simplicity and productivity."
            ),
            stock_count=3,
        ),
        Product(
            name="Pendant Light",
            price=110,
            category="lighting",
            image="pendant-light.jpg",
            description=(
                "Elegant pendant lighting that blends modern design "
                "with functional illumination."
            ),
            stock_count=6,
        ),
        Product(
            name="Leather Notebook",
            price=32,
            category="stationery",
            image="leather-notebook.jpg",
            description=(
                "Premium leather notebook with durable pages for "
                "journaling, planning, and ideas."
            ),
            stock_count=0,
        ),
    ]

    db.session.add_all(products)
    db.session.commit()


with app.app_context():
    db.create_all()
    add_missing_user_columns()
    add_missing_product_columns()
    add_missing_product_report_columns()
    create_demo_admin()
    create_sample_products()


def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def product_image_url(product):
    folder = "images/uploads" if product.seller_id else "images/products"
    return url_for("static", filename=f"{folder}/{product.image}")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            session.clear()
            flash("Please log in to continue.")
            return redirect(url_for("register"))

        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()

        if user is None:
            session.clear()
            flash("Please log in to continue.")
            return redirect(url_for("register"))

        if not user.is_admin:
            flash("Access denied. Administrators only.")
            return redirect(url_for("home"))

        return view(*args, **kwargs)

    return wrapped


@app.context_processor
def shared_template_data():
    cart = session.get("cart", {})
    user = current_user()
    saved_product_ids = set()

    if user:
        saved_product_ids = {
            item.product_id
            for item in WishlistItem.query.filter_by(user_id=user.id).all()
        }

    return {
        "cart_count": sum(cart.values()),
        "current_user": user,
        "saved_product_ids": saved_product_ids,
        "product_image_url": product_image_url,
    }


def is_allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def save_listing_image(upload):
    if not upload or not upload.filename or not is_allowed_image(upload.filename):
        return None

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    extension = secure_filename(upload.filename).rsplit(".", 1)[1].lower()
    filename = f"{uuid4().hex}.{extension}"

    upload.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    return filename


def listing_is_editable(product, user):
    return product.seller_id == user.id or user.is_admin


@app.route("/")
def home():
    page = request.args.get("page", 1, type=int)

    query = (
        Product.query.filter_by(status="approved")
        .order_by(Product.id.desc())
    )

    pagination = query.paginate(page=page, per_page=5, error_out=False)

    return render_template(
        "index.html",
        products=pagination.items,
        pagination=pagination,
    )


@app.route("/shop")
def shop():
    category = request.args.get("category", "all")
    sort = request.args.get("sort", "newest")
    page = request.args.get("page", 1, type=int)

    valid_categories = {"all"} | ALLOWED_CATEGORIES

    if category not in valid_categories:
        category = "all"

    query = Product.query.filter_by(status="approved")

    if category != "all":
        query = query.filter_by(category=category)

    if sort == "price-low":
        query = query.order_by(Product.price.asc())
    elif sort == "price-high":
        query = query.order_by(Product.price.desc())
    else:
        sort = "newest"
        query = query.order_by(Product.id.desc())

    pagination = query.paginate(page=page, per_page=4, error_out=False)

    return render_template(
        "shop.html",
        products=pagination.items,
        pagination=pagination,
        current_category=category,
        current_sort=sort,
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    user = current_user()

    if product.status != "approved" and (
        user is None or not listing_is_editable(product, user)
    ):
        return page_not_found(None)

    return render_template("product.html", product=product)


@app.route("/wishlist")
@login_required
def wishlist():
    items = (
        WishlistItem.query.filter_by(user_id=current_user().id)
        .order_by(WishlistItem.created_at.desc())
        .all()
    )

    return render_template("wishlist.html", items=items)


@app.route("/wishlist/<int:product_id>", methods=["POST"])
@login_required
def toggle_wishlist(product_id):
    product = Product.query.get_or_404(product_id)

    if product.status != "approved":
        return page_not_found(None)

    item = WishlistItem.query.filter_by(
        user_id=current_user().id,
        product_id=product.id,
    ).first()

    if item:
        db.session.delete(item)
        flash("Removed from saved items.")
    else:
        db.session.add(
            WishlistItem(
                user_id=current_user().id,
                product_id=product.id,
            )
        )
        flash("Saved for later.")

    db.session.commit()

    return redirect(request.referrer or url_for("wishlist"))


@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    if product.status != "approved":
        flash(f"{product.name} is no longer available for purchase.")
        return redirect(url_for("shop"))

    if product.stock_count <= 0:
        flash(f"{product.name} is currently out of stock.")
        return redirect(url_for("product_detail", product_id=product.id))

    cart = session.get("cart", {})
    key = str(product.id)
    quantity = cart.get(key, 0)

    if quantity >= product.stock_count:
        flash(f"Only {product.stock_count} of {product.name} are available.")
    else:
        cart[key] = quantity + 1
        session["cart"] = cart
        flash(f"{product.name} was added to your cart.")

    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    cart_data = session.get("cart", {})
    cart_items = []
    total = 0
    changed = False

    for key, quantity in list(cart_data.items()):
        product = db.session.get(Product, int(key))

        if product is None or product.stock_count <= 0:
            cart_data.pop(key, None)
            changed = True
            continue

        safe_quantity = min(quantity, product.stock_count)

        if safe_quantity != quantity:
            cart_data[key] = safe_quantity
            changed = True

        item_total = product.price * safe_quantity
        total += item_total

        cart_items.append(
            {
                "product": product,
                "quantity": safe_quantity,
                "item_total": item_total,
            }
        )

    if changed:
        session["cart"] = cart_data
        flash("Your cart was updated to match current stock availability.")

    return render_template("cart.html", cart_items=cart_items, total=total)


@app.route("/update-cart/<int:product_id>", methods=["POST"])
@login_required
def update_cart(product_id):
    action = request.form.get("action")
    cart_data = session.get("cart", {})
    key = str(product_id)
    product = db.session.get(Product, product_id)

    if product is None or key not in cart_data:
        flash("That product is no longer in your cart.")

    elif action == "increase":
        if cart_data[key] < product.stock_count:
            cart_data[key] += 1
        else:
            flash(f"Only {product.stock_count} of {product.name} are available.")

    elif action == "decrease":
        cart_data[key] -= 1

        if cart_data[key] <= 0:
            cart_data.pop(key)

    elif action == "remove":
        cart_data.pop(key)

    else:
        flash("That cart action is not valid.")

    session["cart"] = cart_data

    return redirect(url_for("cart"))


@app.route("/checkout-simulate", methods=["POST"])
@login_required
def checkout_simulate():
    cart_data = session.get("cart", {})

    if not cart_data:
        flash("Your cart is empty.")
        return redirect(url_for("shop"))

    products = []
    total = 0

    for key, quantity in cart_data.items():
        product = db.session.get(Product, int(key))

        if product is None or quantity < 1 or product.stock_count < quantity:
            available = product.stock_count if product else 0
            name = product.name if product else "an item"

            flash(f"Checkout stopped: {name} has only {available} available.")
            return redirect(url_for("cart"))

        products.append((product, quantity))
        total += product.price * quantity

    order = Order(user_id=current_user().id, total_price=total)

    for product, quantity in products:
        product.stock_count -= quantity

        order.items.append(
            OrderItem(
                product_id=product.id,
                quantity=quantity,
                price_at_purchase=product.price,
            )
        )

    db.session.add(order)
    db.session.commit()

    session.pop("cart", None)

    flash("Purchase successful. Your order and stock levels have been updated.")

    return redirect(url_for("account"))


@app.route("/account")
@login_required
def account():
    user = current_user()

    orders = (
        Order.query.filter_by(user_id=user.id)
        .order_by(Order.order_date.desc())
        .all()
    )

    listings = (
        Product.query.filter_by(seller_id=user.id)
        .order_by(Product.updated_at.desc())
        .all()
    )

    sold_units = sum(
        item.quantity
        for listing in listings
        for item in OrderItem.query.filter_by(product_id=listing.id).all()
    )

    return render_template(
        "account.html",
        user=user,
        orders=orders,
        listings=listings,
        sold_units=sold_units,
    )


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    user = current_user()

    if request.method == "POST":
        today = datetime.utcnow().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        created_today = Product.query.filter(
            Product.seller_id == user.id,
            Product.created_at >= today,
        ).count()

        if created_today >= MAX_LISTINGS_PER_DAY:
            flash(
                f"You can publish up to {MAX_LISTINGS_PER_DAY} listings per day."
            )
            return redirect(url_for("sell"))

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "")
        description = request.form.get("description", "").strip()

        try:
            price = float(request.form.get("price", ""))
            stock_count = int(request.form.get("stock_count", ""))
        except ValueError:
            flash("Price and stock must be valid numbers.")
            return redirect(url_for("sell"))

        image = save_listing_image(request.files.get("image"))

        if not (
            3 <= len(name) <= 100
            and 20 <= len(description) <= 2000
            and category in ALLOWED_CATEGORIES
            and 0 < price <= MAX_PRICE_PER_LISTING
            and 1 <= stock_count <= MAX_STOCK_PER_LISTING
            and image
        ):
            flash(
                "Use a valid name, description, category, price, stock amount, "
                "and JPG, PNG, or WebP image."
            )
            return redirect(url_for("sell"))

        product = Product(
            name=name,
            price=price,
            category=category,
            image=image,
            description=description,
            stock_count=stock_count,
            seller_id=user.id,
            status="pending",
        )

        db.session.add(product)
        db.session.commit()

        flash("Your listing was submitted for administrator review.")

        return redirect(url_for("account"))

    return render_template(
        "sell.html",
        categories=sorted(ALLOWED_CATEGORIES),
        max_stock=MAX_STOCK_PER_LISTING,
    )


@app.route("/sell/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_listing(product_id):
    product = Product.query.get_or_404(product_id)

    if not listing_is_editable(product, current_user()):
        flash("You can only manage your own listings.")
        return redirect(url_for("account"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "")
        description = request.form.get("description", "").strip()

        try:
            price = float(request.form.get("price", ""))
            stock_count = int(request.form.get("stock_count", ""))
        except ValueError:
            flash("Price and stock must be valid numbers.")
            return redirect(url_for("edit_listing", product_id=product.id))

        if not (
            3 <= len(name) <= 100
            and 20 <= len(description) <= 2000
            and category in ALLOWED_CATEGORIES
            and 0 < price <= MAX_PRICE_PER_LISTING
            and 0 <= stock_count <= MAX_STOCK_PER_LISTING
        ):
            flash("Check the name, description, category, price, and stock.")
            return redirect(url_for("edit_listing", product_id=product.id))

        upload = request.files.get("image")

        if upload and upload.filename:
            image = save_listing_image(upload)

            if not image:
                flash("Your replacement image must be JPG, PNG, or WebP.")
                return redirect(url_for("edit_listing", product_id=product.id))

            product.image = image

        product.name = name
        product.category = category
        product.description = description
        product.price = price
        product.stock_count = stock_count
        product.status = "pending"

        db.session.commit()

        flash("Listing updated and sent for review.")

        return redirect(url_for("account"))

    return render_template(
        "edit_listing.html",
        product=product,
        categories=sorted(ALLOWED_CATEGORIES),
        max_stock=MAX_STOCK_PER_LISTING,
    )


@app.route("/sell/<int:product_id>/archive", methods=["POST"])
@login_required
def archive_listing(product_id):
    product = Product.query.get_or_404(product_id)

    if not listing_is_editable(product, current_user()):
        flash("You can only manage your own listings.")
    else:
        product.status = "archived"
        db.session.commit()
        flash("Listing archived.")

    return redirect(url_for("account"))


@app.route("/product/<int:product_id>/report", methods=["POST"])
@login_required
def report_product(product_id):
    product = Product.query.get_or_404(product_id)

    reason = request.form.get("reason", "").strip()
    details = request.form.get("details", "").strip()

    if product.seller_id == current_user().id:
        flash("You cannot report your own listing.")

    elif reason not in {"misleading", "prohibited", "spam", "other"}:
        flash("Choose a valid report reason.")

    elif not 10 <= len(details) <= 1000:
        flash("Provide 10 to 1000 characters of detail.")

    else:
        report = ProductReport(
            product_id=product.id,
            reporter_id=current_user().id,
            reason=reason,
            details=details,
            status="pending",
        )

        db.session.add(report)
        db.session.commit()

        flash("Thanks. Your report has been sent for review.")

    return redirect(url_for("product_detail", product_id=product.id))


@app.route("/edit-account", methods=["GET", "POST"])
@login_required
def edit_account():
    user = current_user()

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        dob_text = request.form.get("dob", "")
        new_password = request.form.get("new_password", "")

        if not first_name or not last_name or not re.match(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            email,
        ):
            flash("Please enter a name and a valid email address.")
            return redirect(url_for("edit_account"))

        if email != user.email and User.query.filter_by(email=email).first():
            flash("That email is already registered.")
            return redirect(url_for("edit_account"))

        try:
            dob = datetime.strptime(dob_text, "%Y-%m-%d").date()
        except ValueError:
            flash("Please enter a valid date of birth.")
            return redirect(url_for("edit_account"))

        if new_password and not re.match(
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$",
            new_password,
        ):
            flash(
                "New password must have at least 8 characters, letters and numbers."
            )
            return redirect(url_for("edit_account"))

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.dob = dob

        if new_password:
            user.password = bcrypt.generate_password_hash(new_password).decode(
                "utf-8"
            )

        db.session.commit()
        session["user_name"] = user.first_name

        flash("Your account details have been updated.")

        return redirect(url_for("account"))

    return render_template("edit_account.html", user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        dob_text = request.form.get("dob", "")

        if not first_name or not last_name or not re.match(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            email,
        ):
            flash("Please complete all fields with a valid email address.")
            return redirect(url_for("register"))

        if not re.match(
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$",
            password,
        ):
            flash(
                "Password must be at least 8 characters and contain letters and numbers."
            )
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists.")
            return redirect(url_for("register"))

        try:
            dob = datetime.strptime(dob_text, "%Y-%m-%d").date()
        except ValueError:
            flash("Please enter a valid date of birth.")
            return redirect(url_for("register"))

        age = datetime.today().year - dob.year - (
            (datetime.today().month, datetime.today().day)
            < (dob.month, dob.day)
        )

        if age < 18:
            flash("You must be at least 18 years old to register.")
            return redirect(url_for("register"))

        user = User(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            email=email,
            password=bcrypt.generate_password_hash(password).decode("utf-8"),
        )

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["user_name"] = user.first_name

        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("login_email", "").strip().lower()
    password = request.form.get("login_password", "")

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["user_name"] = user.first_name

        return redirect(url_for("home"))

    flash("Invalid email or password.")

    return redirect(url_for("register"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.")

    return redirect(url_for("home"))


@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "")
        image = os.path.basename(request.form.get("image", "").strip())
        description = request.form.get("description", "").strip()

        try:
            price = float(request.form.get("price", ""))
            stock_count = int(request.form.get("stock_count", ""))
        except ValueError:
            flash("Price and stock must be valid numbers.")
            return redirect(url_for("admin"))

        if (
            not name
            or not description
            or category not in ALLOWED_CATEGORIES
            or not (0.01 <= price <= MAX_PRICE_PER_LISTING)
            or not (0 <= stock_count <= MAX_STOCK_PER_LISTING)
            or not image
        ):
            flash("Enter valid product information.")
            return redirect(url_for("admin"))

        product = Product(
            name=name,
            price=price,
            category=category,
            image=image,
            description=description,
            stock_count=stock_count,
            is_new="is_new" in request.form,
            is_sale="is_sale" in request.form,
            status="approved",
        )

        db.session.add(product)
        db.session.commit()

        flash(f'Product "{name}" was added to the store.')

        return redirect(url_for("admin"))

    return render_template(
        "admin.html",
        products=Product.query.order_by(Product.id.desc()).all(),
    )


@app.route("/admin/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    if OrderItem.query.filter_by(product_id=product.id).first():
        flash(
            "This product cannot be deleted because it appears in an order."
        )
        return redirect(url_for("admin"))

    db.session.delete(product)
    db.session.commit()

    flash(f'Product "{product.name}" was deleted.')

    return redirect(url_for("admin"))


@app.route("/moderation")
@admin_required
def moderation():
    pending = (
        Product.query.filter_by(status="pending")
        .order_by(Product.created_at.asc())
        .all()
    )

    reports = (
        ProductReport.query.filter_by(status="pending")
        .order_by(ProductReport.created_at.asc())
        .all()
    )

    return render_template(
        "moderation.html",
        pending=pending,
        reports=reports,
    )


@app.route("/moderation/listing/<int:product_id>/<action>", methods=["POST"])
@admin_required
def moderate_listing(product_id, action):
    product = Product.query.get_or_404(product_id)

    if product.status != "pending":
        flash("This listing has already been reviewed.")

    elif action == "approve":
        product.status = "approved"
        db.session.commit()
        flash(f'Listing "{product.name}" was approved.')

    elif action == "reject":
        product.status = "rejected"
        db.session.commit()
        flash(f'Listing "{product.name}" was rejected.')

    else:
        flash("That moderation action is not valid.")

    return redirect(url_for("moderation"))


@app.route("/moderation/report/<int:report_id>/resolve", methods=["POST"])
@admin_required
def resolve_report(report_id):
    report = ProductReport.query.get_or_404(report_id)

    if report.status == "pending":
        report.status = "resolved"
        db.session.commit()
        flash("Report marked as resolved.")
    else:
        flash("This report has already been resolved.")

    return redirect(url_for("moderation"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
