from flask import Flask, render_template, request, jsonify, redirect, session
from eth_account import Account
import random, requests, datetime
from config import *
from database import db


Account.enable_unaudited_hdwallet_features()

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), unique=True, nullable=False)
    mnemonic = db.Column(db.String(300), nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100))
    recipient = db.Column(db.String(100))
    amount_eth = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/wallet', methods=['POST'])
def wallet():
    data = request.get_json()
    action = data.get("action")

    if action == "create":
        acct, mnemonic = Account.create_with_mnemonic()
        address = acct.address
        balance = round(random.uniform(1.0, 10.0), 4)

    elif action == "import":
        mnemonic = data.get("mnemonic")
        if not mnemonic:
            return jsonify({"error": "Mnemonic required for import"}), 400
        acct = Account.from_mnemonic(mnemonic)
        address = acct.address
        balance = 0.0  

    else:
        return jsonify({"error": "Invalid action"}), 400

    
    wallet = Wallet.query.filter_by(address=address).first()
    if not wallet:
        wallet = Wallet(address=address, mnemonic=mnemonic, balance=balance)
        db.session.add(wallet)
        db.session.commit()

    session['address'] = address
    return jsonify({"address": address, "balance": wallet.balance})

@app.route('/dashboard')
def dashboard():
    addr = session.get('address')
    if not addr:
        return redirect('/')
    wallet = Wallet.query.filter_by(address=addr).first()
    return render_template('dashboard.html', wallet=wallet)

@app.route('/transfer')
def transfer_page():
    return render_template('transfer.html')

@app.route('/transfer', methods=['POST'])
def transfer_api():
    data = request.get_json()
    sender_addr = session.get('address')
    if not sender_addr:
        return jsonify({"error": "Wallet not found in session"}), 400

    recipient = data.get("recipient")
    amount = float(data.get("amount", 0))
    currency = data.get("currency")

    if not recipient or amount <= 0:
        return jsonify({"error": "Invalid recipient or amount"}), 400

    if currency == "USD":
        payload = {
            "source_asset_denom": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "source_asset_chain_id": "1",
            "dest_asset_denom": "ethereum-native",
            "dest_asset_chain_id": "1",
            "amount_in": str(amount),
            "chain_ids_to_addresses": {
                "1": "0x742d35Cc6634C0532925a3b8D4C9db96c728b0B4"
            },
            "slippage_tolerance_percent": "1",
            "smart_swap_options": {"evm_swaps": True},
            "allow_unsafe": False
        }
        response = requests.post(
            "https://api.skip.build/v2/fungible/msgs_direct", json=payload
        )
        eth_amount = response.json().get("estimated_amount_out", 0)
        approval_msg = f"Transfer {eth_amount} ETH (${amount} USD) to {recipient} from {sender_addr}"
    else:
        eth_amount = amount
        approval_msg = f"Transfer {eth_amount} ETH to {recipient} from {sender_addr}"

    session['pending_transfer'] = {"recipient": recipient, "amount": eth_amount}
    return jsonify({"approval_message": approval_msg})

@app.route('/confirm_transfer', methods=['POST'])
def confirm_transfer():
    pending = session.get('pending_transfer')
    sender_addr = session.get('address')

    if not pending or not sender_addr:
        return jsonify({"error": "No pending transfer found"}), 400

    sender_wallet = Wallet.query.filter_by(address=sender_addr).first()
    recipient_wallet = Wallet.query.filter_by(address=pending["recipient"]).first()
    amount = pending["amount"]

    if not sender_wallet or sender_wallet.balance < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    if not recipient_wallet:
        recipient_wallet = Wallet(address=pending["recipient"], mnemonic="imported", balance=0)
        db.session.add(recipient_wallet)

    sender_wallet.balance -= amount
    recipient_wallet.balance += amount

    new_tx = Transaction(sender=sender_addr, recipient=pending["recipient"], amount_eth=amount)
    db.session.add(new_tx)
    db.session.commit()

    session.pop('pending_transfer', None)
    return jsonify({"status": "success", "message": "Transfer complete"})

@app.route('/history')
def history():
    addr = session.get('address')
    txs = Transaction.query.filter(
        (Transaction.sender == addr) | (Transaction.recipient == addr)
    ).all()
    return render_template('history.html', txs=txs)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
