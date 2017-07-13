from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import requests
#?page=2&per_page=100
#np.set_printoptions(threshold=np.nan)

class S(BaseHTTPRequestHandler):
	def _set_headers(self):
	    self.send_response(200)
	    self.send_header('Content-type', 'text/html')
	    self.end_headers()

	def do_HEAD(self):
	    self._set_headers()

	def do_GET(self):
		path = self.path
		a=urlparse(path)
		if a.path=='/navigator':
			quer = parse_qs(a.query)
			if quer['search_term']!="":
				term = quer['search_term']
				print(term[0])
				r = requests.get("https://api.github.com/search/repositories?q={0}&page=1&per_page=5".format(term[0]))
				data = r.json()['items']
				data = sorted(data, key=lambda k: k['created_at'], reverse=True)
				start = "<!DOCTYPE html><html><head><title>Github Navigator</title></head><body><h1>{0}</h1>".format(term[0])
				itr = 1
				for i in data:
					commit = requests.get("https://api.github.com/repos/{0}/{1}/commits?page=1&per_page=1".format(i['owner']['login'],i['name']))
					commit = commit.json()
					start = start + "<h2>{0}. {1}</h2> <h3> Created {2}</h3> <a href='{3}'><img src='{4}' alt=\"avatar\" height=\"42\" width=\"42\"/></a>{5}".format(itr,i['name'],i['created_at'],i['owner']['html_url'],i['owner']['avatar_url'],i['owner']['login'])
					start = start +	"<h3>LastCommit</h3> {0} {1}  {2} <hr/>".format(commit[0]['sha'],commit[0]['commit']['message'],commit[0]['commit']['author']['name'])
					itr = itr +1
				
				start = start + "</body></html>"
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				self.wfile.write(bytes(start,"utf-8"))
			else:
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				self.wfile.write(bytes("<!DOCTYPE html><html><head><title>Github Navigator</title></head><body><h1>No term specified</h1></body></html>","utf-8"))
		else:
			self.send_response(404)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(bytes("<html><head>Bad Request</head></html>","utf-8"))


	def do_POST(self):
		self.send_response(404)
		self.send_header('Content-type','text/html')
		self.end_headers()
		self.wfile.write(bytes("<html><head>Bad Request</head></html>","utf-8"))
        
def run(server_class=HTTPServer, handler_class=S, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print ('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
