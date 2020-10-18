from flask import Flask, jsonify, request, Response
from database.db import initialize_db
from database.models import Quote

import json
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
	'host': 'mongodb://localhost/quotes'
}
initialize_db(app)

@app.route('/')
def hello():
	# Quote(quote="hey what's up?", author="12",rating=2,addedBy="12").save()
	return {'hello': 'world'}

@app.route('/quotes')
def get_quotes():
	try:
		quotes = Quote.objects()
		return jsonify({"message":"success", "data": [quote.to_json() for quote in quotes]})
	except Exception as e:
		return Response([json.dumps({"message": "failed", "reason": str(e)})], mimetype="application/json", status=400)

@app.route('/quotes', methods=['POST'])
def add_quote():
	try:
		body = request.get_json()
		quote = Quote(**body).save()
		return {'message': 'success','id': str(quote.id)}, 200
	except Exception as e:
		return {'message': 'failed', "reason": str(e)}, 400

@app.route('/quotes/<id>', methods=['PUT'])
def update_quote_rating(id):
	try:
		body = request.get_json()
		if 'rating' in body:
			Quote.objects.get(id=id).update(set__rating=body.get('rating'))
			return {'message': 'success'}, 200
		else:
			return {'message': 'failed', 'reason': 'Rating missing in request body'}, 400
	except Exception as e:
		return {'message': 'failed', "reason": str(e)}, 400

@app.route('/quotes/user/<id>')
def get_user_quotes(id):
	try:
		quotes = Quote.objects(addedBy=id,rating__ne=None)
		return jsonify({"message":"success", "data": [quote.to_json() for quote in quotes]})
	except Exception as e:
		return Response([json.dumps({"message": "failed", "reason": str(e)})], mimetype="application/json", status=400)

@app.route('/quotes/<id>', methods=['DELETE'])
def delete_quote(id):	
	try:
		Quote.objects.get(id=id).delete()
		return {"message": "success"}, 200
	except Exception as e:
		return {"message": "failed", "reason": str(e)}, 400

@app.route('/related_quote')
def related_quote():	
	try:
		rated_obj = Quote.objects(rating__ne=None)
		unrated_obj = Quote.objects(rating=None)
		rated = [quote.to_json()['quote'] for quote in rated_obj]
		unrated = [quote.to_json()['quote'] for quote in unrated_obj]
		unrated_df = pd.DataFrame({"data":unrated})
		result = []
		if not unrated_df.empty and rated:
			result = unrated_df[unrated_df['data'].apply(lambda x: get_match(x, rated))]['data'].unique()
		return jsonify({"message": "success","data":list(result)})
	except Exception as e:
		return {"message": "failed", "reason": str(e)}, 400

def get_match(data, rated):
	# print(data, rated)
	matched_ratio = process.extract(data,rated, scorer=fuzz.token_sort_ratio)
	if matched_ratio:
		out = list(filter(lambda x: x[1]>50,matched_ratio))
		if out:
			return True
		else:
			return False
	else:
		return False

app.run()
