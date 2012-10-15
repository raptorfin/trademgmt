import ftplib
import logging

def init_ftp(host,user,pwd):
	ftp = ftplib.FTP(host)
	ftp.login(user,pwd)
	return ftp

def change_dir(ftp,_dir):
	ftp.cwd(_dir)

def get_file(ftp,lFile,rFile):
	try:
		with open(lFile,'wb') as f:
			def callback(data):
				f.write(data)
			ftp.retrbinary('RETR %s' % rFile, callback)
		logging.info("Successfully ftp'd %s to %s",rFile,lFile)
	except ftplib.all_errors as ftperror:
		errorcode_string  = str(ftperror).split(None, 1)
		logging.warning("ftp.get_file failed: %s",errorcode_string)
		raise Exception(errorcode_string)

def delete_file(ftp,rFile):
	ftp.delete(rFile)

def close_ftp(ftp):
	ftp.quit()