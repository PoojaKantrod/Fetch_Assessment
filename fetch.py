from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

receipts = {}

@app.route('/receipts/process', methods=['POST'])
def process_receipts():
    try:
        receipt = request.get_json()
        receipt_id = str(uuid.uuid4())
        receipts[receipt_id] = calculate_points(receipt)
        response = {'id': receipt_id}
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    try:
        if receipt_id in receipts:
            points = receipts[receipt_id]
            response = {'points': points}
            return jsonify(response)
        else:
            return jsonify({'error': 'Invalid receipt ID'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_points(receipt):
    points = 0

    try:
        # Rule 1: One point for every alphanumeric character in the retailer name
        points += sum(char.isalnum() for char in receipt['retailer'])

        # Rule 2: 50 points if the total is a round dollar amount with no cents
        if receipt['total'].endswith('.00'):
            points += 50

        # Rule 3: 25 points if the total is a multiple of 0.25
        total = float(receipt['total'])
        if total % 0.25 == 0:
            points += 25

        # Rule 4: 5 points for every two items on the receipt
        num_items = len(receipt['items'])
        points += (num_items // 2) * 5

        # Rule 5: If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer
        for item in receipt['items']:
            description_length = len(item['shortDescription'].strip())
            if description_length % 3 == 0:
                price = float(item['price'])
                item_points = int(round(price * 0.2))
                points += item_points

        # Rule 6: 6 points if the day in the purchase date is odd
        purchase_day = int(receipt['purchaseDate'].split('-')[-1])
        if purchase_day % 2 != 0:
            points += 6

        # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
        purchase_time = receipt['purchaseTime'].split(':')
        hour = int(purchase_time[0])
        minute = int(purchase_time[1])
        if hour > 14 and hour < 16:
            points += 10
    except Exception as e:
        raise ValueError("Invalid receipt format")

    return points

if __name__ == '__main__':
    app.run(debug=True)
