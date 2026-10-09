# Linearfy

## Level 3 Digital Technologies development record

Linearfy is a Flask web application for browsing and purchasing minimalist home, lighting, and stationery products. It was designed for users who want a simple online-shopping experience and for sellers who need to submit, manage, and track their own listings. Administrators can review submitted listings and product reports.

This README explains the completed functionality, the design decisions behind it, the testing that guided improvements, and how GitHub commits document the project's development.

## Purpose and target users

The purpose of Linearfy is to provide a clear, responsive marketplace where users can:

- browse, filter, sort, and paginate approved products;
- register and log in securely;
- add available products to a cart and complete a simulated checkout;
- save products for later;
- submit, edit, and archive their own product listings; and
- report listings that may be misleading, prohibited, or spam.

The intended users are shoppers who want a low-clutter store interface, sellers who need a straightforward way to list products, and an administrator who moderates listings and reports.

## Technology used

| Technology | Use in Linearfy |
| --- | --- |
| Python | Main programming language. |
| Flask | Routes, templates, sessions, form handling, redirects, and error responses. |
| Flask-SQLAlchemy and SQLite | Persistent storage for users, products, orders, order items, reports, and saved items. |
| Flask-Bcrypt | Password hashing and password verification. Plain-text passwords are not stored in the database. |
| Jinja2 | Shared layouts and dynamic pages rendered from Flask data. |
| HTML and CSS | Accessible page structure and the visual interface. |
| JavaScript | Toast notifications, registration feedback, reduced-motion support, page transitions, and prevention of accidental repeated form submission. |
| GitHub | Version control, backups, and evidence of iterative development. |

## Project structure

```text
Linearfy_S.E/
├── app.py                 # Flask routes, data models, validation, access control, and business logic
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/style.css      # Shared visual design and responsive layout rules
│   ├── js/main.js         # Toasts, client-side feedback, and interaction behaviour
│   └── images/
│       ├── products/      # Product images supplied with the application
│       └── uploads/       # Images uploaded with seller listings
└── templates/
    ├── base.html          # Shared navigation, layout, and script loading
    ├── index.html         # Home page
    ├── shop.html          # Product browsing, filters, sorting, and pagination
    ├── product.html       # Product details, cart, save, and report actions
    ├── cart.html          # Cart quantities, total, and checkout
    ├── register.html      # Registration and login
    ├── account.html       # Account, orders, listings, sales, and low-stock information
    ├── admin.html         # Administrator product creation, editing, stock review, and deletion
    ├── sell.html          # Seller listing form
    ├── edit_listing.html  # Seller listing editing
    ├── moderation.html    # Administrator review of listings and reports
    ├── wishlist.html      # Saved products
    ├── edit_account.html  # Account editing
    └── 404.html           # Recovery page for an unknown URL
```

## Database design

The database separates related information into tables so that data is stored once and can be linked when needed.

| Entity | Key information | Relationship and purpose |
| --- | --- | --- |
| `User` | name, date of birth, unique email, hashed password, administrator flag | A user can create listings, place orders, save items, and submit reports. |
| `Product` | name, price, category, image, description, stock, seller, status | A product may be a supplied store product or a listing submitted by a user. Its status controls whether shoppers can view it. |
| `Order` | user, date, total price | Stores the completed purchase for an account. |
| `OrderItem` | order, product, quantity, price at purchase | Resolves the many-to-many relationship between orders and products and preserves the purchase price. |
| `WishlistItem` | user, product, creation time | Stores saved products. A unique user/product constraint prevents duplicate saved items. |
| `ProductReport` | product, reporting user, reason, details, status | Allows users to report a listing and gives an administrator a moderation workflow. |

The `Order` and `OrderItem` design is an important refinement because one order can contain many products and one product can appear in many orders. Storing `price_at_purchase` in `OrderItem` means an older order remains accurate even if the current product price changes later.

## Main functionality and evidence

### Accounts, privacy, and access control

- Registration validates required names, email format, age, password length, and password complexity.
- An email address must be unique, preventing duplicate accounts.
- Passwords are hashed with Bcrypt before storage and checked using Bcrypt during login.
- The session stores the current user ID after successful login.
- `login_required` protects personal features such as the wishlist, seller pages, checkout, and account details.
- `admin_required` checks both that the user is logged in and that their account has the administrator role before allowing moderation or product-administration actions.
- A standard user attempting to reach an administrator route is redirected and shown the message: `Access denied. Administrators only.`
- The administrator panel lets an authorised administrator add products, review product stock and status, edit product details, and delete a product when it has not been included in an order.

### Product browsing and user experience

- The shop supports category filtering, price sorting, and pagination.
- Only products with an `approved` status are shown to normal shoppers.
- Product cards and detail pages show stock availability, including a clear sold-out state and a text-based low-stock indicator when fewer than five items remain.
- Images use descriptive alternative text based on the product name.
- Quantity controls have `aria-label` text, such as “Increase [product name] quantity”, so their purpose is clearer to screen-reader users.
- The notification container uses `aria-live="polite"`, allowing assistive technology to announce feedback without interrupting the user.
- JavaScript respects a user's reduced-motion preference and shows content without animation when that preference is enabled.

### Cart, checkout, and stock integrity

The stock system was refined because restricting the plus button in the browser was not sufficient on its own. The current implementation checks stock at several stages:

1. A product with zero stock cannot be added to the cart.
2. The add-to-cart route prevents the cart quantity from exceeding the product stock count.
3. The cart page corrects saved cart quantities if stock changed after the item was added.
4. The update-cart route prevents the user from increasing a quantity beyond available stock.
5. The checkout route performs a final server-side stock check before creating the order.
6. A successful checkout reduces each product's stock, creates an `Order`, creates related `OrderItem` records, clears the cart, and confirms the result to the user.

This second, server-side validation makes the system more robust because it does not rely only on the browser. It prevents an order from creating negative stock if availability changes before checkout.

### Seller listings and moderation

- A logged-in user can create a listing with a name, category, price, stock amount, image, and detailed description.
- Listing inputs are validated: names must be 3–100 characters, descriptions 20–2,000 characters, prices must be within the permitted range, and stock cannot exceed 999.
- Uploaded images are limited to JPG, PNG, JPEG, and WebP. Filenames are secured and replaced with a generated unique filename.
- New and edited seller listings are marked `pending`, so they cannot appear in the public shop until approved.
- Sellers can edit or archive only their own listings; administrators can manage any listing.
- Users can report a listing, while a seller cannot report their own listing.
- Administrators can approve or reject pending listings and resolve pending reports.

### Error handling and feedback

- An unknown route uses a custom 404 page instead of a default browser error.
- Flash messages are displayed as custom toast notifications for actions such as login failure, a successful cart update, insufficient stock, listing moderation, and access denial.
- Client-side registration checks give immediate feedback for empty fields, weak passwords, and mismatched password confirmation. Flask repeats the important validation on the server, so client-side checks are not the only protection.
- Form submit buttons are temporarily disabled after submission to reduce accidental duplicate checkout, listing, or administration actions.

## Testing and iterative improvement

The table below can be used as evidence of what was tested, what the test showed, and the improvement that resulted. Replace any result with your own exact result or screenshot reference if your teacher asks for direct evidence.

| Area tested | Test action | Result observed | Improvement or conclusion |
| --- | --- | --- | --- |
| Over-purchasing | Added a product until the cart quantity reached the product stock count, then selected the increase/add action again. | The quantity could not exceed available stock and the user received an availability message. | Added stock checks when adding and updating the cart. |
| Stock changing before checkout | Put a product in the cart, reduce its stock in a separate test, then proceed to checkout. | Checkout stops when the requested quantity is higher than current database stock. | Added a final server-side stock check immediately before creating the order. |
| Stock updates after purchase | Completed a checkout with a known product quantity, then reopened the product or account page. | The product stock was reduced by the purchased amount and an order was recorded. | Connected checkout to `Order`, `OrderItem`, and `Product.stock_count` so availability remains accurate. |
| Low-stock threshold | Test products with stock of 5, 4, and 0. | The low-stock indicator is shown for fewer than 5 items; sold-out information appears at 0. | Used both text and visual styling so the warning does not rely on colour alone. |
| Wishlist duplicates | Save the same product more than once. | Only one user/product saved-item record can exist. | Added a unique constraint to prevent duplicate wishlist entries. |
| User account protection | Visit a protected route while logged out. | The application redirects to registration/login and shows a helpful message. | Applied the `login_required` decorator to account-specific functions. |
| Administrator protection | Visit an administrator route using a standard user account. | The application redirects the user and displays an access-denied message. | Applied `admin_required` so users cannot alter administrator-only data. |
| Administrator product management | Log in as an administrator, add a valid product, edit it, then attempt to delete a product that appears in an order. | A valid product is saved; product input is validated; an ordered product is kept to preserve order data. | Connected administrator actions to validation rules and protected order history from losing referenced product data. |
| Listing validation | Submit a listing with invalid price, stock, category, image type, or short description. | The listing is rejected and the user is told what needs correcting. | Added server-side validation and a file-extension allow-list. |
| Moderation | Submit a listing, log in as an administrator, then approve or reject it. | Pending listings can be reviewed; only approved products are visible to shoppers. | Added product status values and the moderation workflow. |
| Reports | Submit a report with an invalid reason or insufficient detail, then submit a valid report. | Invalid reports are rejected; a valid report is saved as `pending` for review. | Added report validation and a pending/resolved status workflow. |
| Unknown page | Enter an address that does not exist, such as `/not-a-real-page`. | The custom 404 page appears instead of a generic error. | Added an error handler and a recovery page. |
| Accessibility feedback | Trigger a toast notification and use keyboard or screen-reader testing where available. | Feedback is written as text, is announced politely, and does not require motion to be understood. | Used `aria-live`, text content, labels, and reduced-motion support. |

## GitHub development evidence

GitHub should show that the project developed through small, purposeful changes. Each commit message should state the completed change and its reason or outcome. It should not use vague messages such as `update`, `changes`, `fixed`, or `final version`.

Use this pattern:

```text
<area>: <specific completed change> - <reason or outcome>
```

Examples that match Linearfy's development are below. Only use a message for a change that you genuinely made in that commit.

| Development stage | Example commit message | Evidence to mention in the GitHub description or assessment log |
| --- | --- | --- |
| Project foundation | `setup: create Flask application with SQLite database models` | Added the application configuration and the core `User`, `Product`, `Order`, and `OrderItem` data structure. |
| Shared design | `ui: add base template and shared navigation for all pages` | Used Jinja2 inheritance so visual and navigation changes are made once in `base.html`. |
| Secure accounts | `auth: validate registration and hash passwords with Bcrypt` | Added email, password, date-of-birth, and duplicate-account validation. |
| Access control | `security: protect account and admin routes with session checks` | Added reusable decorators rather than repeating the same authorisation code in every route. |
| Browsing | `shop: add category filters, sorting, and product pagination` | Made the catalogue easier to browse when more products are present. |
| Cart safety | `cart: prevent quantities from exceeding available stock` | Added stock checks when an item is added or its quantity changes. |
| Robust checkout | `checkout: verify stock server-side and reduce stock after purchase` | Added the second stock check found necessary through over-purchase testing. |
| Order history | `orders: save completed orders and line items to the database` | Preserved the product, quantity, and price at the time of purchase. |
| Stock feedback | `inventory: show low-stock and sold-out states to shoppers` | Tested stock at 5, 4, and 0 to make the threshold unambiguous. |
| Wishlist | `wishlist: prevent duplicate saved products with a unique constraint` | Improved data integrity after testing repeated saves. |
| Seller listings | `listings: validate seller submissions and send them for moderation` | Added validation, safe uploads, a daily listing limit, and a pending status. |
| Moderation | `moderation: allow admins to approve listings and resolve reports` | Added reporting and listing review workflows to address inappropriate or inaccurate content. |
| Feedback | `ux: replace browser alerts with accessible toast notifications` | Provided immediate, non-blocking feedback with `aria-live` support. |
| Error recovery | `errors: add custom 404 page for invalid routes` | Gives users a useful recovery path when they enter an unknown URL. |
| Accessibility | `accessibility: add labels and reduced-motion support` | Improved clarity for screen-reader and motion-sensitive users. |
| Documentation | `docs: document testing outcomes and iterative improvements` | Connected tests to the changes made as a result. |

For every commit you add, include a concise GitHub description or matching log note that answers these three questions:

1. What did I change?
2. Why was that change needed?
3. How did I check it worked?

Example:

> **Commit:** `checkout: verify stock server-side and reduce stock after purchase`  
> **What changed:** I added a final database stock check during checkout and created `Order` and `OrderItem` records after a successful purchase.  
> **Why:** Testing showed that browser-side quantity controls alone could not guarantee stock remained accurate if availability changed before checkout.  
> **How I checked it:** I attempted to buy more items than were available, changed stock before checkout, and completed a valid order. The invalid purchase stopped safely, while the valid purchase reduced stock and appeared in the account order history.

## Relevant implications

### Privacy and security

Passwords are hashed with Bcrypt rather than stored in readable form. Personal account pages and seller features require a logged-in session. Administrator-only routes also check the user's role before allowing a data-changing action. This reduces the chance of a user seeing or altering another user's data.

### Data integrity

The application uses unique email addresses and a unique wishlist user/product pair. Input validation limits values such as price, stock, category, and description length. The checkout process validates current stock on the server before it changes the database. These checks protect against inaccurate data and negative inventory.

### Accessibility and usability

The interface uses labelled controls, descriptive image text, readable status messages, text alongside colour-based stock indicators, and an accessible live-notification area. Reduced-motion support avoids making animation necessary to understand the interface. The custom 404 page and clear flash messages help users recover when an error occurs.

### Social responsibility and content moderation

User-submitted listings start as pending, so they can be reviewed before public display. Users can report a listing, and administrators can resolve reports. Image uploads are restricted to selected image types, and listing text prompts sellers to provide accurate information and confirm that they have the right to share the image.

## Installation and running the project

1. Open a terminal in the `Linearfy_S.E` folder.
2. Create and activate a Python virtual environment if required by your school setup.
3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   python app.py
   ```

5. Open the local URL shown by Flask in a browser.

The application creates its SQLite database and sample products when it first runs. The administrator account defined in the source is for assessment demonstration only; any real deployment would use environment variables and a separately managed administrator account.

## Further refinements identified during code review

The following items are useful next steps and should be completed before describing the outcome as fully finished:

1. Add and test a custom 500 error handler. The current code contains a custom 404 handler only.
2. Turn off Flask debug mode and require the secret key from an environment variable for any deployment beyond assessment demonstration.
3. Add automated tests for critical cases such as stock validation, route protection, duplicate wishlists, listing validation, and moderation status changes.

Completing these refinements would provide further evidence of testing, debugging, and improving the program in response to identified issues.

## Final reflection

Linearfy developed from a basic product catalogue into a more complete marketplace. The largest improvements came from testing the boundaries of stock control, account permissions, duplicate saved items, and seller-submitted content. The outcome now uses server-side validation as well as user-interface feedback, stores linked data in a structured database, protects account-specific features, and gives users clear information when an action succeeds, fails, or requires attention. GitHub commits and this testing record show how each refinement was made in response to a specific need rather than being added without evaluation.
