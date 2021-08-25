import sys
import rlcompleter, readline
readline.parse_and_bind("tab: complete")
import requests
import base64
from time import sleep

XFER_DIR_PATH = 'xfer'
TARGET_HOST = 'http://lizweb-dev:8080'
HEADERS={'Accept': 'application/json', 'Content-Type': 'application/json'}
AUTH=('admin', 'xxxx')

def contentTypes():
	mimes = dict()
	mimes['.bin'] = 'application/octet-stream'
	mimes['.pdf'] = 'application/pdf'
	mimes['.txt'] = 'text/plain'
	mimes['.docx'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
	mimes['.doc'] = 'application/msword'
	mimes['.tex'] = 'text/x-tex'
	mimes['.zip'] = 'application/zip'
	mimes['.tar'] = 'application/x-tar'
	mimes['.csv'] = 'text/comma-separated-values'
	mimes['.xlsx'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
	mimes['.py'] = 'text/x-python'
	mimes['.xls'] = 'application/vnd.ms-excel'
	mimes['.gif'] = 'image/gif'
	mimes['.png'] = 'image/png'
	mimes['.jpg'] = 'image/jpeg'
	mimes['.jar'] = 'application/java-archive'
	#mimes['.jar'] = 'application/x-java-apple'
	return mimes

cTypes = contentTypes()



def uploadFolders():
	f = open(XFER_DIR_PATH + "/folders.idx", "r")
	lines = f.readlines()
	for line in lines:
		#print (line)
		fields = line.split("~~~~~")
		title = fields[0]
		excludeFromNav = fields[1]
		path = fields[2]
		segs = path.split("/")
		id = segs.pop().strip("\n")
		path = ""
		for seg in segs:
			if (len(seg) > 0):
				path = path + "/" + seg
		json={'@type': 'Folder', 'title': title, 'id': id, "exclude_from_nav": excludeFromNav}
		location = TARGET_HOST + path + "/"
		print (line)
		r = requests.get(location + id, headers=HEADERS, auth=AUTH)
		code= r.status_code
		print("check exist response code: ", code)
		if (code == 200):
			print ("folder already exists")
		else:
			print ("new folder! uploading...")
			r = requests.post(location, headers=HEADERS, json=json, auth=AUTH)
			print("upload response code: ", str(r))

	f.close()

def getTextData(path):
	f = open(path, "r")
	txt = f.read()
	return txt

def uploadDocuments():
	f = open(XFER_DIR_PATH + "/docs.idx", "r")
	lines = f.readlines()
	for line in lines:
		#print (line)
		fields = line.split("~~~~~")
		title = fields[0]
		excludeFromNav = fields[1]
		path = fields[2]
		segs = path.split("/")
		id = segs.pop().strip("\n")
		path = ""
		for seg in segs:
			if (len(seg) > 0):
				path = path + "/" + seg
		filepath = XFER_DIR_PATH + path + '/' + id + ".html"
		data = getTextData(filepath)
		location = TARGET_HOST + path + "/"
		print (location + id)

		r = requests.get(location + id, headers=HEADERS, auth=AUTH)
		code= r.status_code
		print("GET: response code: ", code)
		if (code == 200):
			print ("document already exists. Updating...")
			json={'title': title, 'text': data, "exclude_from_nav": excludeFromNav}
			r = requests.patch(location + id, headers=HEADERS, json=json, auth=AUTH)
			print("PATCH response: " + str(r) + "\n")
		else:
			print ("new document. Uploading...")
			json={'@type': 'Document', 'title': title, 'id': id , 'text': data, "exclude_from_nav": excludeFromNav}
			r = requests.post(location, headers=HEADERS, json=json, auth=AUTH)
			print("POST response: " + str(r) + "\n")
			#print(r.content)

	f.close()

def getNewsData(path):
	f = open(path, "r")
	line = f.read()
	item = dict()
	fields = line.split("~~~~~")
	item["title"] = fields[0]
	item["description"] = fields[1]
	item["text"] = fields[2]
	f.close()
	return item

def uploadNewsItems():
	f = open(XFER_DIR_PATH + "/news.idx", "r")
	lines = f.readlines()
	for line in lines:
		print (line)
		#False~~~~~/portal/first-release-of-the-alma-science-pipeline.news
		fields = line.split("~~~~~")
		excludeFromNav = fields[0]
		path = fields[1]
		path = path.strip("\n")
		segs = path.split("/")
		id = segs.pop()
		id = id[:-5]
		print("ID: --- " + id)

		parentPath = ''
		for seg in segs:
			if (len(seg) > 0):
				parentPath = parentPath + "/" + seg

		filepath = XFER_DIR_PATH + path
		print("FILEPATH: " + filepath)
		data = getNewsData(filepath)
		print("PARENTPATH: " + parentPath)
		location = TARGET_HOST + parentPath + "/"
		print("LOCATION: " + location)
		r = requests.get(location + id, headers=HEADERS, auth=AUTH)
		code= r.status_code
		print("GET: response code: ", code)
		if (code == 200):
			print ("news item already exists. Updating...")
			json={'text': data['text'], 'title': data['title'], 'description':data['description'], 'exclude_from_nav': excludeFromNav}
			r = requests.patch(location + id, headers=HEADERS, json=json, auth=AUTH)
			print("PATCH response: " + str(r) + "\n")
		else:
			print ("new News Item. Uploading...")
			json={'@type': 'News Item', 'id': id , 'text': data['text'], 'title': data['title'], 'description':data['description'], 'exclude_from_nav': excludeFromNav}
			r = requests.post(location, headers=HEADERS, json=json, auth=AUTH)
			print("POST response: " + str(r) + "\n")

	f.close()


def getLinkData(path):
	f = open(path, "r")
	line = f.read()
	item = dict()
	line = line.strip("\n")
	fields = line.split("~~~~~")
	item["title"] = fields[0]
	item["remoteUrl"] = fields[1]
	f.close()
	return item

def uploadLinks():
	f = open(XFER_DIR_PATH + "/links.idx", "r")
	lines = f.readlines()
	for line in lines:
		#print (line)
		fields = line.split("~~~~~")
		excludeFromNav = fields[0]
		path = fields[1]
		segs = path.split("/")
		id = segs.pop().strip("\n")
		path = ""
		for seg in segs:
			if (len(seg) > 0):
				path = path + "/" + seg
		filepath = XFER_DIR_PATH + path + '/' + id 
		data = getLinkData(filepath)
		print(str(data))
		id = id[:-5]
		location = TARGET_HOST + path + "/"
		print (location + id)
		r = requests.get(location + id, headers=HEADERS, auth=AUTH)
		code= r.status_code
		print("GET: response code: ", code)
		if (code == 200):
			print ("Link already exists. Updating...")
			json={'title': data['title'], 'remoteUrl': data['remoteUrl'], "exclude_from_nav": excludeFromNav}
			r = requests.patch(location + id, headers=HEADERS, json=json, auth=AUTH)
			print("PATCH response: " + str(r) + "\n")
		else:
			print ("new link. Uploading...")
			json={'@type': 'Link', 'title': data['title'], 'id': id , 'remoteUrl': data['remoteUrl'], "exclude_from_nav": excludeFromNav}
			r = requests.post(location, headers=HEADERS, json=json, auth=AUTH)
			print("POST response: " + str(r) + "\n")

	f.close()


def uploadFiles(ploneType, idxFilePath, datatype):
	f = open(XFER_DIR_PATH + "/" + idxFilePath, "r")
	lines = f.readlines()
	for line in lines:
		fields = line.split("~~~~~")
		excludeFromNav = fields[0]
		#print (line)
		segs = fields[1].split("/")
		id = segs.pop().strip("\n")
		path = ""
		for seg in segs:
			if (len(seg) > 0):
				path = path + "/" + seg
		#print (path)
		rf = id.rfind(".")
		lid = len(id)
		lastdot = lid - rf
		extension = id[0-lastdot:]		
		try: 
			mimetype = cTypes[extension]
			filepath = XFER_DIR_PATH + path + '/' + id
			#remove redundant file extension
			ploneid = id[0:rf]
			print("ploneid: " + ploneid)
			imgfile = open(filepath, 'rb')
			data = imgfile.read()
			enc = base64.b64encode(data)
			dec = enc.decode('utf-8')
			data ={ "data": dec, "encoding": "base64", "filename": ploneid,"content-type": mimetype}
			location = TARGET_HOST + path + "/"
			print("URL :" + location + ploneid)
			#print("FILE: " + filepath)

			r = requests.get(location + ploneid, headers=HEADERS, auth=AUTH)
			code= r.status_code
			#print("GET: response code: ", code)
			if (code == 200):
				print (ploneType + " already exists. Updating...")
				json={'title': ploneid, datatype: data, 'exclude_from_nav': excludeFromNav}
				r = requests.patch(location + ploneid, headers=HEADERS, json=json, auth=AUTH)
				code= r.status_code
				if (code != 204):
					print("PATCH response: " + str(code))
					print("URL: " + location + ploneid)
					print("FILE: " + filepath)
			else:
				print ("new " + ploneType + ". Uploading...")
				json={'@type': ploneType, 'title': ploneid, 'id': ploneid, datatype: data, 'exclude_from_nav': excludeFromNav}
				r = requests.post(location, headers=HEADERS, json=json, auth=AUTH)
				code= r.status_code
				if (code != 201):
					print("POST response: " + str(code))
					print("text: " + str(r.text))
					print("URL: " + location + ploneid)
					print("FILE: " + filepath + "\n")

		except Exception as e:
			print("UNKNOWN MIME TYPE?: [" + extension + "] ")
			print("PATH: " + path)
			print("Exception: " + str(e))
			print(" ")

	f.close()

#uploadFolders()
uploadDocuments()
#uploadFiles('Image', 'images.idx', 'image')
#uploadFiles('File', 'files.idx', 'file')
#uploadNewsItems()
#uploadLinks()


