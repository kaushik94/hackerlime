import sublime, sublime_plugin
import urllib2, httplib, urllib
import json as JSON

import re

import base64

username = ''
password = ''
master_url = 'https://www.hackerrank.com/rest/contests/'


lang = {'py':'python', 'java':'java', 'c':'c', 'cpp':'cpp'}

class CustomBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
	'''
	Preemptive basic auth.

	Instead of waiting for a 403 to then retry with the credentials,
	send the credentials if the url is handled by any password manager.
	Note: please use realm=None when calling add_password.

	'''
	def http_request(self, req):
		url = req.get_full_url()
		realm = None
		# this is very similar to the code from retry_http_basic_auth()
		# but returns a request object.
		user, pw = self.passwd.find_user_password(realm, url)
		if pw:
			raw = "%s:%s" % (user, pw)
			auth = 'Basic %s' % base64.b64encode(raw).strip()
			req.add_unredirected_header(self.auth_header, auth)
		return req

	https_request = http_request

class RunCodeCommand(sublime_plugin.TextCommand):
   
   def run(self, edit):

	  payload, url, code, custom_testcase = self.get_params()

	  # print url
	  sock = urllib2.Request(url+'compile_tests', urllib.urlencode(payload))
	  resp = urllib2.urlopen(sock)
	  header = resp.read()
	  # print header
	  header_ = JSON.loads(header)
	  id_ =  header_['model']['id']
	  sock = urllib2.Request(url+'compile_tests/'+str(id_)+'?')
	  resp = urllib2.urlopen(sock)
	  self.pretty_print(id_, code, JSON.loads(resp.read()), custom_testcase)

   def get_params(self):

	  auth_handler = CustomBasicAuthHandler()
	  auth_handler.add_password( realm=None, uri=master_url, user=username, passwd=password)
	  opener = urllib2.build_opener(auth_handler)
	  urllib2.install_opener(opener)

	  language, code, custom_testcase, child_url = self.get_file_info()
	  if custom_testcase is None:
		payload = {'code':code, 'customtestcase':'false', 'language':language}
	  else:
	  	payload = {'code':code, 'customtestcase':'true', 'language':language, 'custominput':custom_testcase}
	  return payload, master_url+child_url, code, custom_testcase

   def get_file_info(self):
	  ffname = self.view.file_name()
	  file_name = ffname.split('/')[-1]
	  extension = file_name.split('.')[-1]
	  language = lang[extension]

	  code, custom_testcase = self.get_code(language)
	  juice = code.split('\n')[-1] 	  
	  contester = map(str, juice.split())[-1]
	  contester = contester.split('/')
	  if contester[3] == 'challenges':
		child_url = "master/challenges/"+contester[-1]+"/"
	  else:
		child_url = contester[4]+"/challenges/"+contester[-1]+"/"
	  return language, code, custom_testcase, child_url

   def get_code(self, language):

	  content = self.view.substr(sublime.Region(0, self.view.size()))
	  testcases = self.load_tests(content, language)
	  if testcases is not None:
	  	print testcases
	  	return content, testcases
	  return content, None

   def pretty_print(self, id_, code, result, custom_testcase):

	  
	  print "\n"+'SUBMISSION ID:', str(id_)+"\n"
	  print "YOUR CODE"+"\n"
	  print code+"\n"
	  print "RESULT:" 
	  result_list = result['model']['testcase_message']
	  print ''.join('	TESTCASE '+str(index+1)+": "+str(each)+'\n' for index, each in enumerate(result_list))

	  if custom_testcase is not None:
	  	print "CUSTOM TEST RESULT\n"
	  	print "INPUT"
	  	for each in result['model']['stdin']:
	  		print str(each)
	  	print "OUTPUT"
	  	for each in result['model']['stdout']:
	  		print str(each)

   def pylang_tests(self, content):
	    m = re.findall('"""T\n(.*?)\nT"""', content, re.DOTALL)
	    if len(m):
	    	return m[0]
	    return None
   def reg_tests(self, content):
	    m = re.findall('/*T\n(.*?)\nT*/', content, re.DOTALL)
	    return None
   def load_tests(self, content, language):
	    if language is 'python':
	    	return self.pylang_tests(content)
	    elif language in ['c', 'cpp', 'java']:
			return self.reg_tests(content)
