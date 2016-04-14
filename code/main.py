import json
import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import multiprocessing as mp
import urllib
import cgi
import urllib2
import re

data = []
keywordIndex = {}
smalldata = []

# sys.setdefaultencoding('utf-8')

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
		# reqPath = self.path.split("?query=")
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
			try: 
				article_id = int(args["article_id"][0])
				print "OK"
				URL = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&q="+urllib.quote_plus(re.sub(' +',' ',data[article_id]["keywords"].encode("ascii", "ignore")))+"&key=AIzaSyDlfXZ-dnk4K87LDNaTigVQwZ8i233bb8s&maxResults=10&type=video"
				print URL
				content = urllib2.urlopen(URL).read()
				videos = extract_links(content)
				query = re.sub(r'\W+', '', data[article_id]["url"])
				URL = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&q="+urllib.quote_plus(query)+"&key=AIzaSyDlfXZ-dnk4K87LDNaTigVQwZ8i233bb8s&maxResults=10&type=video"
				content = urllib2.urlopen(URL).read()
				videos.extend(extract_links(content))
				self.wfile.write(json.dumps(videos))
			except KeyError:
				query = re.sub(r'\W+', '', data[article_id]["url"])
				URL = "https://www.googleapis.com/youtube/v3/search?part=id,snippet&q="+urllib.quote_plus(query)+"&key=AIzaSyDlfXZ-dnk4K87LDNaTigVQwZ8i233bb8s&maxResults=10&type=video"
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
		# smalldata.append({"index": textID, "title": parsed_line["title"], "content": parsed_line["text"][0:50]})
		textID += 1
	# print data[0]["keywords"]
	print notfound
	c = mp.Process(target=run_server)				# HTTP server process
	c.start()

	# while 1:
		# pass

def extract_links(content):
	content = json.loads(content)
	videos = []
	for video in content["items"]:
		videos.append(video["id"]["videoId"])
	return videos




if __name__ == "__main__":
	init(sys.argv[1])