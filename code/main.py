import json
import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import multiprocessing as mp
import urllib
import cgi
import urllib2
import re

stopWords = []
data = []
keywordIndex = {}
smalldata = []

# sys.setdefaultencoding('utf-8')

def translate(word, to_langage="auto", langage="auto"):
	agents = {'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
	before_trans = 'class="t0">'
	link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_langage, langage, word.replace(" ", "+"))
	request = urllib2.Request(link, headers=agents)
	page = urllib2.urlopen(request).read()
	result = page[page.find(before_trans)+len(before_trans):]
	result = result.split("<")[0]
	return result

'''
Handler for the integrated web server interface
'''
class S(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()


	'''
	Handles GET requests for the server
	'''
	def do_GET(self):
		self._set_headers()
		args = {}
		idx = self.path.find('?')
		if idx >= 0:
			rpath = self.path[:idx]
			args = cgi.parse_qs(self.path[idx+1:])
		else:
			rpath = self.path

		if rpath == '/search':										# If the request is for a search process, read the query term.
			# reqPath[1] = urllib.unquote(reqPath[1]).decode('utf8')		# For URL decoding
			# self.wfile.write(json.dumps(results))
			pass
		elif rpath == '/':											# Request for homepage
			self.wfile.write(open('index.html').read())	
		elif rpath == '/getList':
			last = args.get("last", 0)
			self.wfile.write(json.dumps(data[int(last[0]):20+int(last[0])]))
		elif rpath == '/getVideos':
			article_id = int(args["article_id"][0])
			print "OK"
			if not data[article_id].has_key("processed"):
				original_title=data[article_id]["title"].strip().strip('"').encode('utf-8')
				title_keywords = ""
				for each in original_title.split(' '):
					if each not in stopWords:
						title_keywords += " " + each
				flag=0
				while flag<=5:
					try:
						title_keywords=translate(title_keywords)
						# print flag + " got "+title_keywords
						flag+=1
					except:
						continue
				title_keywords.replace(' ',',')
				data[article_id]["title"]=title_keywords
			else:
				title_keywords = data[article_id]["title"]
			data[article_id]["processed"] = True
			print data[article_id]["title"]
			try: 
				print "Using Title: "+title_keywords
				URL = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&q="+urllib.quote_plus(title_keywords)+"&key=AIzaSyDlfXZ-dnk4K87LDNaTigVQwZ8i233bb8s&maxResults=10&type=video"
				content = urllib2.urlopen(URL).read()
				videos = extract_links(content)

				URL = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&q="+urllib.quote_plus(re.sub(' +',' ',data[article_id]["keywords"].encode("ascii", "ignore")))+"&key=AIzaSyDlfXZ-dnk4K87LDNaTigVQwZ8i233bb8s&maxResults=10&type=video"
				print URL
				content = urllib2.urlopen(URL).read()
				videos.extend(extract_links(content))

				query = re.sub(r'\W+', '', data[article_id]["url"])
				URL = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&q="+urllib.quote_plus(query)+"&key=AIzaSyDlfXZ-dnk4K87LDNaTigVQwZ8i233bb8s&maxResults=10&type=video"
				content = urllib2.urlopen(URL).read()
				videos.extend(extract_links(content))

				self.wfile.write(json.dumps(videos))
			except KeyError:
				print "Using Title: "+title_keywords
				URL = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&q="+urllib.quote_plus(title_keywords)+"&key=AIzaSyDlfXZ-dnk4K87LDNaTigVQwZ8i233bb8s&maxResults=10&type=video"
				content = urllib2.urlopen(URL).read()
				videos = extract_links(content)
				self.wfile.write(json.dumps(videos))
		else:															# Request for all other files
			self.wfile.write(open(rpath[1:]).read())

	def do_HEAD(self):
		self._set_headers()
		
	def do_POST(self):
		# Doesn't do anything with posted data
		self._set_headers()
		self.wfile.write("<html><body><h1>POST requests are not needed for this service!</h1></body></html>")
		
'''
Starts the HTTP server
'''
def run_server(server_class=HTTPServer, handler_class=S, port=5005):
	server_address = ('0.0.0.0', port)
	httpd = server_class(server_address, handler_class)
	print 'Starting httpd...'
	httpd.serve_forever()




def init(filename):
	fp = open('hi.stop', 'r') 
	global stopWords
	for line in fp.readlines():
		stopWords.append(line.strip('\n'))
	fp = open(filename, 'r')
	global data
	global keywordIndex
	global smalldata
	textID = 0
	notfound = 0
	for line in fp.readlines():
		parsed_line = json.loads(line)
		try:
			curr_keywords = parsed_line["keywords"].split(',')
			for each in curr_keywords:
				if keywordIndex.has_key(each):
					keywordIndex[each].append(textID)
				else:
					keywordIndex[each] = [textID]
		except KeyError:
			notfound += 1
		parsed_line["id"] = textID
		data.append(parsed_line)
		textID += 1
	print notfound
	c = mp.Process(target=run_server)				# HTTP server process
	c.start()

def extract_links(content):
	content = json.loads(content)
	videos = []
	for video in content["items"]:
		videos.append(video["id"]["videoId"])
	return videos




if __name__ == "__main__":
	init(sys.argv[1])
