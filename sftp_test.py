#!/usr/bin/env python

import pysftp as sftp

def sftpExample():
	try:
		s = sftp.Connection(host='10.36.10.37', username='sftp', password='test123', log="./temp/pysftp.log")

		remotepath = 'import/nvOS-3.0.4-3000413315-onvl.pkg'
		localpath = '/Users/pierregi/python/netpy/nvOS-3.0.4-3000413315-onvl.pkg'
		s.put(localpath,remotepath)

		s.close()

	except Exception, e:
		print str(e)

if __name__=='__main__':
	sftpExample()
