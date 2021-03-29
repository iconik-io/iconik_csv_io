#import required libraries
import json 
import requests
import csv
import configargparse
import os
import getpass
import datetime as dt 

#build our csv arguments
parser = configargparse.ArgParser(default_config_files=['config.ini'],description='Import/Export metadata using CSV Files')
parser.add('-c','--config_file',is_config_file=True,help="Path to custom config file")
parser.add('-m','--mode',type=str,help="Must be either 'collection' or 'saved_search' or 'search'")
parser.add('-s','--search_terms',type=str,help="Search string")
parser.add('-v','--metadata_view',type=str,help="UUID of metadata view you want to work with",required=True)
parser.add('-a','--app_id',type=str,help="iconik App-ID")
parser.add('-t','--auth_token',type=str,help="iconik Auth Token")
parser.add('-i','--input_file',type=str,help="Properly formatted importable CSV file")
parser.add('-o','--output_dir',type=str,help="Destination for exported CSV directory")
cli_args = parser.parse_args()

#validate our inputs, exit if they don't appear valid
if cli_args.input_file is not None and cli_args.output_dir is not None:
	print("You've set both an input and export file, please only choose one")
	exit()

if cli_args.input_file is None and cli_args.output_dir is None:
	print("You've set no inputs or outputs, please choose one")
	exit()


if cli_args.input_file is not None:
	if not os.path.isfile(cli_args.input_file):
		print('Input file could not be found, exiting.')
		exit()
	else:
		job_mode = "Input"

if cli_args.output_dir is not None:
	if not os.path.isdir(cli_args.output_dir):
		print('Output file directory could not be found, exiting.')
		exit()
	elif cli_args.mode is None or cli_args.search_terms is None:
		print('Attempting to output but no mode or search string specified')
		exit()
	else:
		job_mode = "Output"

if cli_args.mode is not None:
	if cli_args.mode == "search":
		if cli_args.search_terms is None:
			print('You have to provide search terms if your mode is "search"')

if cli_args.app_id is None or cli_args.auth_token is None:
	auth_method = "simple"
else:
	auth_method = "api"

#format our iconik headers for quick use - this means using the simple auth endpoint to get our appID/token if none are specified
#if no one has set app id or token in CLI or config, let's ask for a username and password
if auth_method == "simple":
	print("No App ID or Token specified in CLI or config file, assuming standard auth")
	username = input("iconik username: ")
	password = getpass.getpass("iconik password: ")
	r = requests.post('https://app.iconik.io/API/auth/v1/auth/simple/login/',headers={'accept':'application/json','content-type':'application/json'},data=json.dumps({'app_name':'WEB','email':username,'password':password}))
	if r.status_code == 201:
		app_id = r.json()['app_id']
		auth_token = r.json()['token']
	else:
		print('Auth failed - status code ' + str(r.status_code))
		for error in r.json()['errors']:
			print(error)
		exit()
#if app_id and token are set, use them and bypass simple auth		
else:
	app_id = cli_args.app_id
	auth_token = cli_args.auth_token

#just set some global values we'll use further down
headers = {'App-ID':app_id,'Auth-Token':auth_token,'accept':'application/json','content-type':'application/json'}
iconik_url = 'https://app.iconik.io/API/'

#build some of the functions we'll use for this script

#get a column list from a metadata view for our CSV file
def get_csv_columns_from_view(metadata_view):
	r = requests.get(iconik_url + 'metadata/v1/views/' + metadata_view,headers=headers)
	if r.status_code == 200:
		csv_columns = []
		for field in r.json()['view_fields']:
			if field['name'] != "__separator__":
				csv_columns.append(field['name'])
		return csv_columns
	else:
		print("Error Fetching Metadata View ID " + metadata_view)
		for error in r.json()['errors']:
			print(error)
		exit()

# get all results in a saved search, return the full object list with metadata
def get_saved_search_assets(saved_search_id):
	r = requests.get(iconik_url + 'search/v1/search/saved/' + saved_search_id,headers=headers)
	if r.status_code == 200:
		search_doc = r.json()['search_criteria_document']['criteria']
	else:
		print("Error Fetching Saved Search ID " + saved_search_id)
		for error in r.json()['errors']:
			print(error)
			exit()

	search_doc['metadata_view_id'] = cli_args.metadata_view

	r = requests.post(iconik_url + 'search/v1/search/',headers=headers,data=json.dumps(search_doc),params={'per_page':'150','scroll':'true','generate_signed_url':'false','save_search_history':'false'})
	if r.status_code == 200:
		results = r.json()['objects']
		while len(r.json()['objects']) > 0:
			r = requests.post(iconik_url + 'search/v1/search',headers=headers,params={'scroll':'true','scroll_id':r.json()['scroll_id']},data=json.dumps(search_doc))
			results = results + r.json()['objects']
	return results

# get all results from a search query and return the full object list with metadata
def get_search_assets(search_terms):
	search_doc = {"doc_types": ["assets"], "query": search_terms, "metadata_view_id": cli_args.metadata_view}
	r = requests.post(iconik_url + 'search/v1/search/',headers=headers,data=json.dumps(search_doc),params={'per_page':'150','scroll':'true','generate_signed_url':'false','save_search_history':'false'})
	if r.status_code == 200:
		results = r.json()['objects']
		while len(r.json()['objects']) > 0:
			r = requests.post(iconik_url + 'search/v1/search',headers=headers,params={'scroll':'true','scroll_id':r.json()['scroll_id']},data=json.dumps(search_doc))
			results = results + r.json()['objects']
		return results
	else:
		print("Error Running Search with terms " + cli_args.search_terms)
		for error in r.json()['errors']:
			print(error)
			exit()

# get all results from a collection and return the full object list with metadata
def get_collection_assets(collection_id):
	search_doc = {"doc_types": ["assets"], "query": "", "metadata_view_id": cli_args.metadata_view,"filter":{"operator":"AND","terms":[{"name":"in_collections","value":collection_id}]}}
	r = requests.post(iconik_url + 'search/v1/search/',headers=headers,data=json.dumps(search_doc),params={'per_page':'150','scroll':'true','generate_signed_url':'false','save_search_history':'false'})
	if r.status_code == 200:
		results = r.json()['objects']
		while len(r.json()['objects']) > 0:
			r = requests.post(iconik_url + 'search/v1/search',headers=headers,params={'scroll':'true','scroll_id':r.json()['scroll_id']},data=json.dumps(search_doc))
			results = results + r.json()['objects']
		return results
	else:
		print("Error listing collection with id " + cli_args.search_terms)
		for error in r.json()['errors']:
			print(error)
			exit()

# update iconik metadata
def update_metadata(asset_id,metadata_doc):
	r = requests.put(f"{iconik_url}/metadata/v1/assets/{asset_id}/views/{cli_args.metadata_view}/",data=json.dumps(metadata_doc),headers=headers)
	if r.status_code == 200:
		print(f"Successfully updated asset {asset_id} metadata")
	else:
		print(f"Error updating metadata for asset {asset_id}")
		for error in r.json()['errors']:
			print(error)
		print(f"Metadata was not updated")

# update iconik asset title
def update_title(asset_id,title_doc):
	r = requests.patch(f"{iconik_url}/assets/v1/assets/{asset_id}/",data=json.dumps(title_doc),headers=headers)
	if r.status_code == 200:
		print(f"Successfully updated asset {asset_id} title")
	else:
		print(f"Error updating title for asset {asset_id}")
		for error in r.json()['errors']:
			print(error)
		print(f"Title was not updated")

# build a CSV file
def build_csv_file(iconik_results,metadata_field_list):
	#get today's date and time 
	today = dt.datetime.now().strftime("%m-%d-%Y %Hh%Mm%Ss")
	filename = f"{cli_args.search_terms} - {today}.csv"
	#open our CSV file
	with open(cli_args.output_dir + '/' + filename,'w',newline='') as csvfile:
		metadata_file = csv.writer(csvfile,delimiter=',',quotechar='"')
		#write our header row
		metadata_file.writerow(['id','title'] + metadata_field_list)
		columns=len(metadata_field_list)
		#loop through all assets
		for asset in iconik_results:
			#get metadata per asset
			row = []
			row.append(asset['id'])
			row.append(asset['title'])
			for _ in range(columns):
				try:
					if isinstance(asset['metadata'][metadata_field_list[_]],list):
						row.append(','.join(map(str,asset['metadata'][metadata_field_list[_]])))
					else:
						row.append(asset['metadata'][metadata_field_list[_]])
				except:
					row.append("")
			metadata_file.writerow(row)
		print(f"File successfully saved to {cli_args.output_dir}/{filename}")
		return True

# read a csv file, turn into iconik metadata, update iconik
def read_csv_file(input_file):
	#open our CSV file
	with open(input_file,newline='') as csvfile:
		#create our CSV reader
		metadata_reader = csv.reader(csvfile,delimiter=',',quotechar='"')
		#read the first row of the file to get the field names
		fields = next(metadata_reader)
		#loop through each row of the CSV
		for row in metadata_reader:
			#create our dicts for titles and metadata
			this_title={}
			this_metadata = {'metadata_values':{}}
			#loop over each value in the row
			#determine if it is a multi-value
			#format metadata and do a put to update each row
			for count,value in enumerate(row):
				# first column is always our asset id
				if count == 0:
					asset_id = value
				# second column is always our title
				elif count == 1:
					this_title = {'title':value}
				# columns after that are our metadata and variable in length
				elif count > 1:
					this_metadata['metadata_values'][fields[count]] = {}
					this_metadata['metadata_values'][fields[count]]['field_values'] = []
					#turn all values into lists (even if only one item)
					field_values = value.split(",")
					#check if only one item
					if len(field_values) > 0:
						for field_value in field_values:
							#check if there is even anything in the column
							if field_value != "":
								#if metadata in column, update
								this_metadata['metadata_values'][fields[count]]['field_values'].append({'value':field_value})
							else:
								#if metadata not in column, remove the key
								del this_metadata['metadata_values'][fields[count]]

			# send update for title
			update_title(row[0],this_title)
			# send update for metadata				
			update_metadata(row[0],this_metadata)
	return True
			
if job_mode == "Input":
	read_csv_file(cli_args.input_file)
elif job_mode == "Output":
	if cli_args.mode == 'saved_search':
		assets = get_saved_search_assets(cli_args.search_terms)
	elif cli_args.mode == 'collection':
		assets = get_collection_assets(cli_args.search_terms)
	elif cli_args.mode == 'search':
		assets = get_search_assets(cli_args.search_terms)
	else:
		print(f"I don't know what {cli_args.mode} means.  Exiting.")
		exit()	
	if build_csv_file(assets,get_csv_columns_from_view(cli_args.metadata_view)):
		print(f"Script finished successfully")
		exit()
	else:
		print(f"We ran into an error somewhere")
else:
	print(f"You have managed to divide by zero and create a singularity - run!")
	exit()