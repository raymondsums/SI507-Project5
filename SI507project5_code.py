## import statements
import requests_oauthlib
import webbrowser
import json
import secret_data
from datetime import datetime
import csv

## CACHING SETUP

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True
CACHE_FNAME = "cache_contents.json"
CREDS_CACHE_FILE = "creds.json"

try:
	with open(CACHE_FNAME,'r') as cache_file:
		cache_json = cache_file.read()
		CACHE_DICTION = json.loads(cache_json)
except:
	CACHE_DICTION = {}

try:
	with open(CREDS_CACHE_FILE,'r') as creds_file:
		cache_creds = creds_file.read()
		CREDS_DICTION = json.loads(cache_creds)
except:
	CREDS_DICTION = {}

def has_cache_expired(timestamp_str, expire_in_days):
	now = datetime.now()
	cache_timestamp = datetime.strptime(timestamp_str,DATETIME_FORMAT)

	delta = now - cache_timestamp
	delta_in_days = delta.days

	if delta_in_days > expire_in_days:
		return True
	else:
		return False

def get_from_cache(identifier, dictionary):
	identifier = identifier.upper()
	if identifier in dictionary:
		data_assoc_dict = dictionary[identifier]
		if has_cache_expired(data_assoc_dict['timestamp'],data_assoc_dict['expire_in_days']):
			if DEBUG:
				print("Cache has expired for {}".format(identifier))
			del dictionary[identifier]
			data = None
		else:
			data = dictionary[identifier]['values']
	else:
		data = None
	return data

def set_in_data_cache(identifier,data,expire_in_days):
	identifier = identifier.upper()
	CACHE_DICTION[identifier] = {
		'values':data,
		'timestamp':datetime.now().strftime(DATETIME_FORMAT),
		'expire_in_days': expire_in_days
	}

	with open(CACHE_FNAME, 'w') as cache_file:
		cache_json = json.dumps(CACHE_DICTION)
		cache_file.write(cache_json)

def set_in_creds_cache(identifier, data, expire_in_days):
	identifier = identifier.upper()
	CREDS_DICTION[identifier] = {
		'values' : data,
		'timestamp' : datetime.now().strftime(DATETIME_FORMAT),
		'expire_in_days' : expire_in_days
	}

	with open(CREDS_CACHE_FILE, 'w') as cache_file:
		cache_json = json.dumps(CREDS_DICTION)
		cache_file.write(cache_json)

## ADDITIONAL CODE for program should go here...
## Perhaps authentication setup, functions to get and process data, a class definition... etc.
'''
def get_data_from_api(request_url,service_ident,params_diction, expire_in_days=7):
	ident = create_request_identifier(request_url,params_diction)
	data = get_from_cache(ident,CACHE_DICTION)
	if data:
		if DEBUG:
			print("Loading from data cache: {}... data".format(ident))
	else:
		if DEBUG:
			print("Fetching new data from {}".format(request_url))
'''

CLIENT_KEY = secret_data.client_key
CLIENT_SECRET = secret_data.client_secret

REQUEST_TOKEN_URL = "https://www.tumblr.com/oauth/request_token" 
BASE_AUTH_URL = "https://www.tumblr.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://www.tumblr.com/oauth/access_token"

def get_tokens(client_key=CLIENT_KEY,client_secret=CLIENT_SECRET,request_token_url=REQUEST_TOKEN_URL,base_authorization_url=BASE_AUTH_URL,access_token_url=ACCESS_TOKEN_URL,verifier_auto=True):
	oauth_inst = requests_oauthlib.OAuth1Session(client_key,client_secret=client_secret)
	fetch_response = oauth_inst.fetch_request_token(request_token_url)

	resource_owner_key = fetch_response.get('oauth_token')
	resource_owner_secret = fetch_response.get('oauth_token_secret')

	auth_url = oauth_inst.authorization_url(base_authorization_url)
	webbrowser.open(auth_url)

	if verifier_auto:
		verifier = input("Please input the verifier:  ")
	else:
		redirect_result = input("Paste the full redirect URL here:  ")
		oauth_resp = oauth_inst.parse_authorization_response(redirect_result)
		verifier = oauth_resp.get('oauth_verifier')

	oauth_inst = requests_oauthlib.OAuth1Session(client_key,client_secret=client_secret,resource_owner_key=resource_owner_key,resource_owner_secret=resource_owner_secret, verifier=verifier)
	oauth_tokens = oauth_inst.fetch_access_token(access_token_url)

	resource_owner_key, resource_owner_secret = oauth_tokens.get('oauth_token'), oauth_tokens.get('oauth_token_secret')
	return client_key, client_secret, resource_owner_key, resource_owner_secret, verifier

def get_tokens_from_service(service_name_ident, expire_in_days = 7):
	creds_data = get_from_cache(service_name_ident, CREDS_DICTION)
	if creds_data:
		if DEBUG:
			print("Loading creds from cache...")
			print()

	else:
		if DEBUG:
			print("Fetching fresh credentials...")
			print("Prepare to log in via browser.")
			print()
		creds_data = get_tokens()
		set_in_creds_cache(service_name_ident, creds_data, expire_in_days=expire_in_days)
	return creds_data

def create_request_identifier(url, params_diction):
	total_ident = url + "?api_key=" + params_diction
	return total_ident.upper()

def get_data_from_api(request_url, service_ident, params_diction, expire_in_days=7):
	ident = create_request_identifier(request_url, params_diction)
	print(ident)
	data = get_from_cache(ident, CACHE_DICTION)
	if data :
		if DEBUG:
			print("Loading from data cache: {}... data".format(ident))
	else:
		if DEBUG:
			print("Fetching new data from {}".format(request_url))
		client_key, client_secret, resource_owner_key, resource_owner_secret,verifier = get_tokens_from_service(service_ident)

		oauth_inst = requests_oauthlib.OAuth1Session(client_key, client_secret=client_secret, resource_owner_key=resource_owner_key,resource_owner_secret=resource_owner_secret)
		resp = oauth_inst.get(request_url,params = params_diction)
		data_str = resp.text
		data = json.loads(data_str)
		set_in_data_cache(ident, data, expire_in_days)
	return data

if __name__ == "__main__":
	if not CLIENT_KEY or not CLIENT_SECRET:
		print("You need to fill in client_key and client_secret in the secret_data.py file")
		exit()
	if not REQUEST_TOKEN_URL or not BASE_AUTH_URL:
		print("You need to fill in this API's specific OAuth2 URLs in this file.")
		exit()

	tumblr_photo_search_baseurl = "https://api.tumblr.com/v2/blog/newsweek.tumblr.com/posts/photo"
	tumblr_text_search_baseurl = "https://api.tumblr.com/v2/blog/newsweek.tumblr.com/posts/text"

tumblr_photo_result = get_data_from_api(tumblr_photo_search_baseurl,"api_key",CLIENT_KEY)
photo_dict = tumblr_photo_result
photo_id_list = []
photo_timestamp_list = []
photo_tags_list = []
photo_url_list = []
photo_width_list = []
photo_height_list = []
for i in photo_dict['response']['posts']:
	photo_id_list.append(i['id'])
	photo_timestamp_list.append(i['timestamp'])
	photo_tags_list.append(i['tags'])
	for j in i['photos']:
		photo_url_list.append(j['original_size']['url'])
		photo_width_list.append(j['original_size']['width'])
		photo_height_list.append(j['original_size']['height'])
photo_dimensions_list = []
for i in range(len(photo_width_list)):
	photo_dimensions_list.append(str(photo_width_list[i]) + " x " + str(photo_height_list[i]))

tumblr_text_result = get_data_from_api(tumblr_text_search_baseurl,"api_key",CLIENT_KEY)
text_dict = tumblr_text_result['response']['posts']
text_id_list = []
text_date_list = []
text_timestamp_list = []
text_title_list = []
text_content_list = []
text_tags_list = []
for i in text_dict:
	text_id_list.append(i['id'])
	text_date_list.append(i['date'])
	text_timestamp_list.append(i['timestamp'])
	text_title_list.append(i['title'])
	text_tags_list.append(i['tags'])
	for j in i['trail']:
		text_content_list.append((j['content']).strip('/n'))

## Make sure to run your code and write CSV files by the end of the program.

outfile_photo = open("tumblr_photo.csv","w")
outfile_photo.write('"id","timestamp","tags","url","dimensions"\n')
for i in range(len(photo_dict['response']['posts'])):
	outfile_photo.write('"{}","{}","{}","{}","{}"\n'.format(photo_id_list[i],photo_timestamp_list[i],photo_tags_list[i],photo_url_list[i],photo_dimensions_list[i]))
outfile_photo.close()

outfile_text = open("tumblr_text.csv","w")
with open('tumblr_text.csv','w') as outfile_text:
	writer = csv.writer(outfile_text)
	outfile_text.write('"id","date","timestamp","title","tags","content"\n')
	for i in range(len(text_dict)):
		writer.writerow([text_id_list[i],text_date_list[i],text_timestamp_list[i],text_title_list[i],text_tags_list[i],text_content_list[i]])
outfile_text.close()
