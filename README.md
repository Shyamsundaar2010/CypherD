Web3 Wallet Walkthrough

Home Page
•	Choose to Create Wallet or Import Wallet.
•	If creating, copy and save your 12-word mnemonic.

Dashboard
•	View your wallet address and ETH balance.
•	Access Send Transfer and Transaction History pages.

Send Transfer
•	Enter recipient address and amount (ETH or USD).
•	Generate approval message.
•	Confirm transfer to update balances.

Transaction History
•	See all past transfers you sent or received.

How to Set Up the Project

Step 1: Clone the repository
https://github.com/Shyamsundaar2010/CypherD.git

Step 2: Install dependencies
pip install Flask Flask-SQLAlchemy psycopg2-binary requests eth-account

Step 3: Setup PostgreSQL
•	Open pgAdmin or PostgreSQL CLI.
•	Create a database, e.g., wallet_db.
•	Update the config.py file with your database credentials
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:”YOUR_PASSWORD”@localhost/wallet_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

Step 4: Initialize the database
•	Run the following in Python:
  from app import db, ap
  with app.app_context():
    db.create_all()

This will create the Wallet and Transaction tables.

Step 5: Run the Flask App
python app.py
Visit http://127.0.0.1:5000/ in your browser.

