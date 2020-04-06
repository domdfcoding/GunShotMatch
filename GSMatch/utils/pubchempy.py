"""
PubChemPy

Python interface for the PubChem PUG REST service.
Adapted from https://github.com/mcs07/PubChemPy
"""


# stdlib
import json
import logging
import time
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import urlopen

# 3rd party
from chemistry_tools.constants import API_BASE, text_types
from chemistry_tools.errors import PubChemHTTPError
from chemistry_tools.lookup import get_compounds

get_compounds = get_compounds

__author__ = 'Matt Swain'
__email__ = 'm.swain@me.com'
__version__ = '1.0.4'
__license__ = 'MIT'


log = logging.getLogger('pubchempy')
log.addHandler(logging.NullHandler())


def request(identifier, namespace='cid', domain='compound', operation=None, output='JSON', searchtype=None, **kwargs):
	"""
	Construct API request from parameters and return the response.

	Full specification at http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html
	"""
	
	if not identifier:
		raise ValueError('identifier/cid cannot be None')
	# If identifier is a list, join with commas into string
	if isinstance(identifier, int):
		identifier = str(identifier)
	if not isinstance(identifier, text_types):
		identifier = ','.join(str(x) for x in identifier)
	# Filter None values from kwargs
	kwargs = {k: v for k, v in kwargs.items() if v is not None}
	# Build API URL
	urlid, postdata = None, None
	if namespace == 'sourceid':
		identifier = identifier.replace('/', '.')
	if namespace in ['listkey', 'formula', 'sourceid'] \
			or searchtype == 'xref' \
			or (searchtype and namespace == 'cid') or domain == 'sources':
		urlid = quote(identifier.encode('utf8'))
	else:
		postdata = urlencode([(namespace, identifier)]).encode('utf8')
	comps = filter(None, [API_BASE, domain, searchtype, namespace, urlid, operation, output])
	apiurl = '/'.join(comps)
	if kwargs:
		apiurl += '?%s' % urlencode(kwargs)
	# Make request
	try:
		log.debug('Request URL: %s', apiurl)
		log.debug('Request data: %s', postdata)
		response = urlopen(apiurl, postdata)
		return response
	except HTTPError as e:
		raise PubChemHTTPError(e)


def get(identifier, namespace='cid', domain='compound', operation=None, output='JSON', searchtype=None, **kwargs):
	"""
	Request wrapper that automatically handles async requests.
	"""
	
	if (searchtype and searchtype != 'xref') or namespace in ['formula']:
		response = request(identifier, namespace, domain, None, 'JSON', searchtype, **kwargs).read()
		status = json.loads(response.decode())
		if 'Waiting' in status and 'ListKey' in status['Waiting']:
			identifier = status['Waiting']['ListKey']
			namespace = 'listkey'
			while 'Waiting' in status and 'ListKey' in status['Waiting']:
				time.sleep(2)
				response = request(identifier, namespace, domain, operation, 'JSON', **kwargs).read()
				status = json.loads(response.decode())
			if not output == 'JSON':
				response = request(identifier, namespace, domain, operation, output, searchtype, **kwargs).read()
	else:
		response = request(identifier, namespace, domain, operation, output, searchtype, **kwargs).read()
	return response
