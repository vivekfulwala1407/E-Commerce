Overview

This is a Django-based e-commerce web application designed to handle product management, user authentication, cart operations, order processing, and admin functionalities. The project provides a RESTful API interface for frontend integration or testing via tools like Postman.

Installation

1. Clone the Repository

git clone https://github.com/vivekfulwala1407/E-Commerce.git
cd ecommerce

2. Install Dependencies

Create a virtual environment and install the required packages:

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3. Set Up the Database

Apply migrations to set up the database:

python manage.py makemigrations

python manage.py migrate

4. Create a Superuser

Create an admin user for testing admin features:

python manage.py createsuperuser

5. Run the Development Server

Start the Django development server:

python manage.py runserver
