#!/usr/bin/env python2.7

from bottle import *

import transmissionrpc

@get('/')
def index():
	return r'''<html><body>'sup.<br><br><form method="post">Magnet: <input name="magnet"> <input type="submit" value="go get it"></form></body></html> '''


@post('/')
def posted():
	magnet = request.forms.get('magnet')
	if magnet[:7] != 'magnet:': abort(400, "Whatcha talkin' bout willis?! That's no magnet link")

	# Okay, it looks a bit like a magnet link
	tc = transmissionrpc.Client()
	try:
		torrent = tc.add_torrent(magnet,peer_limit=1024)
		# Globally limited already hopefully
		torrent.download_limit = 5000 # 5MBytes/s
		torrent.upload_limit = 2000 # 2MBytes/s
	except:
		# The problem *might* be that it's already in there.
		try:	
			# this will fail  if it's not realy in there
			return redirect('/'+gettorrentfrommagnet(magnet).hashString)
		except: pass
		abort(400, "That's a broken looking magnet you got there. Come back when you picked up a real one: %s" % repr(magnet))

	# Okay, hash string. Yay.
	redirect('/'+torrent.hashString)

@get('/all')
def list_all():
	tc = transmissionrpc.Client()
	torrents = tc.get_torrents()
	out = '<html><body><ul>'
	for v in torrents:
		out += '<li><a href="/%s">%s</a><br>(%s) (%s) %s\n<br><br>' % (v.hashString,v,v.status,v.progress,"(eta "+v.format_eta()+")" if v.eta > 0 else "")
	return out + '</ul></body></html>'

@get('/favicon.ico')
def favico():
	return ""

def gettorrentfromhash(hashthingy):
	tc = transmissionrpc.Client()
	torrents = tc.get_torrents()
	for v in torrents:
		if v.hashString == hashthingy: return v

def gettorrentfrommagnet(magnet):
	'''try to match the hash of an existing torrent to the hash'''
	tc = transmissionrpc.Client()
	torrents = tc.get_torrents()
	for v in torrents:
		if len(v.hashString) > 10 and v.hashString in str(magnet):
			return v
	
@get('/<hashstring>/<fileid>')
def getcompletefile(hashstring,fileid):
	tc = transmissionrpc.Client()
	try:
		torrent = gettorrentfromhash(hashstring)
		files = torrent.files()
		filedetails = files[int(fileid)]
	except Exception as e:
		abort(400, "Go home torrent. You're drunk. %s" % repr(e))
	completed,size = filedetails['completed'],filedetails['size']
	if completed < size:
		return "%d%%\n\n\n%s" % ((completed *100)  / size,str(torrent))
	# Okay, everything seems legit here.
	from os import system
	# Take care of the uploading to trove
	system('s3cmd -P sync ~/Downloads s3://fetchme')
	redirect('http://fetchme.beta.anchortrove.com/Downloads/%s' % (filedetails['name']))

def show_files_in_torrent(torrent):
	hashthingy = torrent.hashString
	out = '<html><body><ul>'
	for k,v in torrent.files().items():
		out+= '<li><a href="/%s/%s">%s</a>' % (hashthingy,k,v['name'])
	out+= '</body></html>'
	return out

@get('/<hashstring>')
def getcomplete(hashstring):
	tc = transmissionrpc.Client()
	try:
		torrent = gettorrentfromhash(hashstring)
	except Exception as e:
		abort(400, "Go home hash string. You're drunk. %s"%repr(e))

	if torrent.status == 'seeding':
		return show_files_in_torrent(torrent)

	return '<html><body><h1>%s</h1><h2>Torrent is %s and %s%% done. ETA is %s.</h2></body></html>' %  (torrent,torrent.status,torrent.progress,torrent.format_eta())

if __name__ == "__main__":
	run(host='0.0.0.0')
else:
	application = default_app()
