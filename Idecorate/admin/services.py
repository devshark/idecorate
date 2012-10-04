import os

def getExtensionAndFileName(filename):

	filename, extension = os.path.splitext(filename)

	return (filename, extension)