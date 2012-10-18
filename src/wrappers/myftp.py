import ftplib
import logging

LOGGER = logging.getLogger(__name__)
NOFILE_ERROR = 'Failed to open file'

def init_ftp(host, user, pwd):
	ftp = ftplib.FTP(host)
	ftp.login(user, pwd)
	LOGGER.info("Connected to: %s", host)
	return ftp


def change_dir(ftp, dir_):
	ftp.cwd(dir_)
	LOGGER.info("Changed dir to: %s", dir_)


def list_dir(ftp):
	return ftp.retrlines('LIST')


def get_file(ftp, l_file, r_file):
	try:
		LOGGER.info("Retrieving remote file: %s", r_file)
		with open(l_file, 'wb') as f:
			def callback(data):
				f.write(data)
			ftp.retrbinary('RETR %s' % r_file, callback)
		LOGGER.info("Successfully ftp'd %s to %s", r_file, l_file)
		return True
	except ftplib.all_errors as err:
		LOGGER.warning("get_file failed: %s", err)
		if NOFILE_ERROR in str(err):
			return False
		else:
			raise Exception(err)


def delete_file(ftp, file_):
	ftp.delete(file_)
	LOGGER.info("Deleted file: %s", file_)


def close_ftp(ftp):
	ftp.quit()
