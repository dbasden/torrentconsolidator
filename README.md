The Totally-Legitimate-And-Above-Board-Debian-ISO-Torrent-Downloader

Thrown together in an hour or so for the Anchor Trove hackfest.

This presents a web form which takes a torrent magnet link. The
webapp then gets transmission-daemon to download the files referenced
by the magnet, showing a refreshable progress display.

When the download is complete, a list of links to files are shown.
When you click on one of the files, it makes sure all the downloaded
files are synced to the storage backend, and then redirects you to
the actual file.

The upshot of this is that you give the magic box a magnet link and
get files out

Requirements:
	- transmission-daemon running
	- s3cmd configured

Bugs:
	- Many

Security:
	- None
