#
# download_species_images.py
#
# Downloads all images of each species in species_images.json
# 
# Adapted from download_lila_subset.py
#

# Constants and imports

import json
import urllib.request
import tempfile
import os

from tqdm import tqdm
from urllib.parse import urlparse

# LILA camera trap master metadata file
metadata_url = 'http://lila.science/wp-content/uploads/2020/03/lila_sas_urls.txt'

# JSON filename
# json_filename = "species_images.json"
json_filename = "empty_images.json"

# Don't change this for now - we are only downloading from Snapshot Serengeti
dataset = 'Snapshot Serengeti'

# We'll write images here
output_dir = 'Downloads'
os.makedirs(output_dir,exist_ok=True)

# In case the program crashes
downloaded_species = []


# Support functions

def download_url(url, destination_filename=None, force_download=False, verbose=True):
    """
    Download a URL (defaulting to a temporary file)
    """
    if destination_filename is None:
        temp_dir = os.path.join(tempfile.gettempdir(),'lila')
        os.makedirs(temp_dir,exist_ok=True)
        url_as_filename = url.replace('://', '_').replace('.', '_').replace('/', '_')
        destination_filename = \
            os.path.join(temp_dir,url_as_filename)
            
    if (not force_download) and (os.path.isfile(destination_filename)):
        print('Bypassing download of already-downloaded file {}'.format(os.path.basename(url)))
        return destination_filename
    
    if verbose:
        print('Downloading file {} to {}'.format(os.path.basename(url),destination_filename),end='')
    
    os.makedirs(os.path.dirname(destination_filename),exist_ok=True)

    exception = False
    try:
        urllib.request.urlretrieve(url, destination_filename)  
    except:
        print("An exception occurred")
        print("Failed url:", url)
        exception = True
    
    if not exception:
        assert(os.path.isfile(destination_filename))
        if verbose:
            nBytes = os.path.getsize(destination_filename)    
            print('...done, {} bytes.'.format(nBytes))
        
    return destination_filename


def download_relative_filename(url, output_base, species_name, verbose=False):
    """
    Download a URL to output_base, preserving relative path
    """
    
    p = urlparse(url)
    # remove the leading '/'
    assert p.path.startswith('/'); relative_filename = p.path[1:]

    # Get rid of many subfolders
    relative_filename = relative_filename.split('/')[-1]

    destination_filename = os.path.join(output_base, species_name, relative_filename)
    download_url(url, destination_filename, verbose=verbose)

# -------------------------------------------------------------------

# Download and parse the metadata file

p = urlparse(metadata_url)
metadata_filename = os.path.join(output_dir,os.path.basename(p.path))
download_url(metadata_url, metadata_filename)

# Read lines from the master metadata file
with open(metadata_filename,'r') as f:
    metadata_lines = f.readlines()
metadata_lines = [s.strip() for s in metadata_lines]

# Parse those lines into a table
metadata_table = {}

for s in metadata_lines:
    
    if len(s) == 0 or s[0] == '#':
        continue
    
    # Each line in this file is name/sas_url/json_url
    tokens = s.split(',')
    assert len(tokens)==3
    url_mapping = {'sas_url':tokens[1],'json_url':tokens[2]}
    metadata_table[tokens[0]] = url_mapping
    
    assert 'https' not in tokens[0]
    assert 'https' in url_mapping['sas_url']
    assert 'https' in url_mapping['json_url']

# Parse sas url
sas_url = metadata_table[dataset]['sas_url']

base_url = sas_url.split('?')[0]    
assert not base_url.endswith('/')
    
sas_token = sas_url.split('?')[1]
assert not sas_token.startswith('?')

# Open species_images.json
with open(json_filename, 'r') as f:
    data = json.load(f)

for species_name in data:
    if species_name not in downloaded_species:
        urls_to_download = [base_url + '/' + im['file_name'] for im in data[species_name]]
        print(f"Found {len(urls_to_download)} urls to download for species: {species_name}")
        print("Downloading now...")
        for url in tqdm(urls_to_download):
            download_relative_filename(url, output_dir, species_name, verbose=True)