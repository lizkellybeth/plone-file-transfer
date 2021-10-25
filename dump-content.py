import sys
import rlcompleter, readline
readline.parse_and_bind("tab: complete")
import os
from plone.outputfilters.browser.resolveuid import uuidToURL
site = app.portal
catalog = site.portal_catalog
brains =catalog.unrestrictedSearchResults(sort_on='path', sort_order='ascending')
cwd = os.getcwd()
XFER_DIR_PATH = cwd + "/xfer"

def mimeTypes():
	mimes = dict()
	mimes['application/octet-stream'] = '.bin'
	mimes['application/pdf'] = '.pdf'
	mimes['text/plain'] = '.txt'
	mimes['application/vnd.openxmlformats-officedocument.wordprocessingml.document'] = '.docx'
	mimes['application/msword'] = '.doc'
	mimes['text/x-tex'] = '.tex'
	mimes['application/zip'] = '.zip'
	mimes['application/x-tar'] = '.tar'
	mimes['text/comma-separated-values'] = '.csv'
	mimes['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'] = '.xlsx'
	mimes['text/x-python'] = '.py'
	mimes['application/vnd.ms-excel'] = '.xls'
	mimes['image/png'] = '.png'
	mimes['image/jpeg'] = '.jpg'
	mimes['application/java-archive'] = '.jar'
	mimes['application/x-java-apple'] = '.jar'
	return mimes

mimeTypes = mimeTypes()

# https://www.peterbe.com/plog/zope-image-to-filesystem-image
def writeBlobToFile( source, temp_file ):
   """
   - source : a zope brain.getObject() - (not just a string with the object id!!)
   - temp_file : a writable file object
   """
   data = source.data
   #if isinstance(data, String): #doesn't work with python2... 
   if isinstance(data, basestring):
       temp_file.write( data )
   else:
       (start,end) = (0,source.getSize())
       pos = 0
       while source.data is not None:
           l =  len(data.data)
           pos = pos + l
           if pos > start:
               # We are within the range
               lstart = l - (pos - start)
               if lstart < 0: lstart = 0
               # find the endpoint
               if end <= pos:
                   lend = l - (pos - end)
                   temp_file.write(data[lstart:lend])
                   break
               # Not yet at the end, transmit what we have.
               temp_file.write(data[lstart:])
           data = data.next
   temp_file.flush()
   temp_file.seek(0, 0)

#open the idx files...
docfile = open(XFER_DIR_PATH + "/docs.idx", "w")
imgfile = open(XFER_DIR_PATH + "/images.idx", "w")
filefile = open(XFER_DIR_PATH + "/files.idx", "w")
linkfile = open(XFER_DIR_PATH + "/links.idx", "w")
newsfile = open(XFER_DIR_PATH + "/news.idx", "w")


#make the folder structure...
f1 = open(XFER_DIR_PATH + "/folders.idx", "w")
for child in brains:
    obj = child.getObject()
    id = obj.id
    title = obj.getRawTitle()
    tipe = obj.getPortalTypeName()
    path = child.getPath()
    hide = str(obj.getRawExcludeFromNav())

    if ('Folder' == tipe):
        #print tipe, path
	out = XFER_DIR_PATH + path
	if not os.path.exists(out):
		os.makedirs(out)
	f1.write(title + "~~~~~" + hide + "~~~~~" + path + "\n")
f1.flush()
f1.close()

# eg.  href="resolveuid/40a86d35ffa94e10a2ffb7e27a16c4ec"
def replaceUIDs(raw):
	idx = raw.find('resolveuid/', 0)
	while (idx > -1):
		uidBegin = idx + 11
		uidEnd = uidBegin + 32
		uidUrl = raw[idx:uidEnd]
		#print ("uidUrl: " +  uidUrl)
		uid = raw[uidBegin:uidEnd]
		url = uuidToURL(uid)
		#print ("url: "+  str(url))
		if (url is not None):
			#relUrl = uidUrl.replace("resolveuid/","") 
			relUrl = url.replace("http://nohost","") 
			#print ("relUrl: " +  relUrl)
			raw = raw.replace(uidUrl, relUrl)
		else: 
			print ("URL NOT FOUND FOR UID: [" + uid + "] IN [" + path + "]")
			raw = raw.replace(uidUrl, "#")
		idx = raw.find('resolveuid/', 0)		
		#print ("\n")
	return raw
	
for child in brains:
    obj = child.getObject()
    id = obj.id
    path = child.getPath()
    title = obj.getRawTitle()
    #print(path)
    tipe = obj.getPortalTypeName()
    hide = str(obj.getRawExcludeFromNav())

    if ('Document' == tipe):
	out = XFER_DIR_PATH + path + ".html"
        raw = obj.getRawText()
	raw = replaceUIDs(raw)
	f = open(out, "w")
	f.write(raw)
	f.close()
	docfile.write(title + "~~~~~" + hide + "~~~~~" + path + "~~~~~" + tipe + "\n")

    if ('File' == tipe):
	contenttype = obj.getContentType()
	try:
		extension = mimeTypes[contenttype]
		out = XFER_DIR_PATH + path + extension
		f = open(out, "w")
		writeBlobToFile( obj, f )
		f.close()
		filefile.write(hide + "~~~~~" + path + extension + "\n")

	except:
		print("UNKNOWN MIME TYPE: [" + contenttype + "] ")
		print("PATH: " + path)
		print(" ")

    if ('Image' == tipe):
		path = child.getPath()
		out = XFER_DIR_PATH + path
		bw = obj.getImage()
		contenttype = bw.getContentType()
		if ('jpeg' in contenttype): 
		    out = out + ".jpg"
		    imgfile.write(hide + "~~~~~" + path + ".jpg\n")
		elif ('png' in contenttype): 
		    out = out + ".png"
		    imgfile.write(hide + "~~~~~" + path + ".png\n")
		elif ('gif' in contenttype): 
		    out = out + ".gif"
		    imgfile.write(hide + "~~~~~" + path + ".gif\n")
		else:
	    	    print("UNKNOWN IMAGE TYPE: [" + contenttype + "] ")
	    	    print("PATH: " + path)
	    	    print(" ")
		    continue

		f = open(out, "w")
		writeBlobToFile( obj, f )
		f.close()

    if ('Link' == tipe):
	out = XFER_DIR_PATH + path + ".link"
    	#print("Link: " + out + "\n")
        remoteURL = obj.getRawRemoteUrl()
        title = obj.getRawTitle()
		# ceUIDseg.  href="resolveuid/40a86d35ffa94e10a2ffb7e27a16c4ec"
    	f = open(out, "w")
    	line = title + "~~~~~" + remoteURL + "\n"
    	f.write(line)
    	f.close()
	linkfile.write(hide + "~~~~~" + path + ".link\n")

    if ('News Item' == tipe):
	out = XFER_DIR_PATH + path + ".news"
        title = obj.getRawTitle()
    	text = obj.getRawText()
	text = replaceUIDs(text)
    	desc = obj.getRawDescription()
	f = open(out, "w")
	content = title + "~~~~~" + desc + "~~~~~" + text + "\n"
	f.write(content)
	f.close()
	newsfile.write(hide + "~~~~~" + path + ".news\n")

	#there are only 3 Topics in the portal. Skip it.
    if ('Topic' == tipe):
    	print("Topics will not be transferred: " + path + "\n")

	#there is only a single (obsolete) Event in the portal. Skip it.
    if ('Event' == tipe):
    	print("Events will not be transferred: " + path + "\n")

	#there is only a single (obsolete) FormFolder in the portal. Skip it.
    if ('FormFolder' == tipe):
    	print("FormFolders will not be transferred: " + path + "\n")



docfile.flush()
docfile.close()
imgfile.flush()
imgfile.close()
filefile.flush()
filefile.close()
linkfile.flush()
linkfile.close()
newsfile.flush()
newsfile.close()

print("Done!")
