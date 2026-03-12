# Final Project for the API course by META on Coursera

API project for a restaurant including the major topics  of the course.

## Key Features

### Authentication & Security
* User registration and **Token-based Authentication** via Djoser.
* Role-Based Access Control (**RBAC**):
  * **Managers:** Full menu control and staff management.
  * **Delivery Crew:** View and update assigned orders.
  * **Customers:** Browse menu, manage cart, and place orders.
* **Throttling:** Implemented rate limiting to protect the API from excessive requests.

  ### Menu Management
* Robust endpoints to list, create, update, and delete menu items.
* Support for **Pagination**, **Category Filtering**, and **Price Ordering**.
* Data integrity ensured with unique title validation at the Serializer level.

### Cart & Order Logic
* Intelligent cart system that calculates total prices server-side (preventing client-side price manipulation).
* Automated conversion from Cart items to a finalized Order with auto-calculated totals and timestamps.
* Automatic cart clearing upon successful order placement.

## Tech Stack

* **Python 3.x**
* **Django 4.x**
* **Django REST Framework**
* **Djoser** (Token Auth)
* **SQLite** (Database


##  Getting Started


1. **Clone the repository:**
   
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME

3. **Set up a virtual environment:**
   
   python -m venv venv
   
   On Windows:
   
  .\venv\Scripts\activate
  
   On Mac/Linux:
   
  source venv/bin/activate

5. **Install dependencies:**
   
  pip install django djangorestframework djoser

7. **Initialize the database:**
   
  python manage.py makemigrations
  python manage.py migrate

9. **Create an Admin (Superuser)::**
    
  python manage.py createsuperuser

11. **Run the server:**
    
  python manage.py runserver
   
