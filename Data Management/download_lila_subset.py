#
# download_lila_subset.py
#
# Example of how to download a list of files from LILA, e.g. all the files
# in a data set corresponding to a particular species.
#

# Constants and imports

import json
import urllib.request
import tempfile
import zipfile
import os

from tqdm import tqdm
from multiprocessing.pool import ThreadPool
from urllib.parse import urlparse

# LILA camera trap master metadata file
metadata_url = 'http://lila.science/wp-content/uploads/2020/03/lila_sas_urls.txt'

# In this example, we're using the Missouri Camera Traps data set and the Caltech Camera Traps dataset
datasets_of_interest = ['Snapshot Serengeti']

# All lower-case; we'll convert category names to lower-case when comparing
species_of_interest = ['leopard', 'rhinoceros', 'waterbuck']

# We'll write images, metadata downloads, and temporary files here
output_dir = 'test'
os.makedirs(output_dir,exist_ok=True)

# We will demonstrate two approaches to downloading, one that loops over files
# and downloads directly in Python, another that uses AzCopy.
#
# AzCopy will generally be more performant and supports resuming if the 
# transfers are interrupted.  It assumes that azcopy is on the system path.
use_azcopy_for_download = False

overwrite_files = False

# Number of concurrent download threads (when not using AzCopy) (AzCopy does its
# own magical parallelism)
n_download_threads = 1


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
    

def unzip_file(input_file, output_folder=None):
    """
    Unzip a zipfile to the specified output folder, defaulting to the same location as
    the input file    
    """
    
    if output_folder is None:
        output_folder = os.path.dirname(input_file)
        
    with zipfile.ZipFile(input_file, 'r') as zf:
        zf.extractall(output_folder)

# -------------------------------------------------------------------

# Download and parse the metadata file

# Put the master metadata file in the same folder where we're putting images
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


# Download and extract metadata for the datasets we're interested in

for ds_name in datasets_of_interest:
    
    assert ds_name in metadata_table
    json_url = metadata_table[ds_name]['json_url']
    
    p = urlparse(json_url)
    json_filename = os.path.join(output_dir,os.path.basename(p.path))
    download_url(json_url, json_filename)
    
    # Unzip if necessary
    if json_filename.endswith('.zip'):
        
        with zipfile.ZipFile(json_filename,'r') as z:
            files = z.namelist()
        assert len(files) == 1
        unzipped_json_filename = os.path.join(output_dir,files[0])
        if not os.path.isfile(unzipped_json_filename):
            unzip_file(json_filename,output_dir)        
        else:
            print('{} already unzipped'.format(unzipped_json_filename))
        json_filename = unzipped_json_filename
    
    metadata_table[ds_name]['json_filename'] = json_filename
    
# -------------------------------------------------------------------

# ...for each dataset of interest


# List of files we're going to download (for all data sets)

# Flat list or URLS, for use with direct Python downloads
urls_to_download = {}

# For use with azcopy
downloads_by_dataset = {}

for ds_name in datasets_of_interest:
    
    json_filename = metadata_table[ds_name]['json_filename']
    sas_url = metadata_table[ds_name]['sas_url']
    
    base_url = sas_url.split('?')[0]    
    assert not base_url.endswith('/')
    
    sas_token = sas_url.split('?')[1]
    assert not sas_token.startswith('?')
    
    ## Open the metadata file
    
    with open(json_filename, 'r') as f:
        data = json.load(f)
    
    categories = data['categories']
    for c in categories:
        c['name'] = c['name'].lower()
    category_id_to_name = {c['id']:c['name'] for c in categories}
    annotations = data['annotations']
    images = data['images']


    ## Build a list of image files (relative path names) that match the target species

    category_ids = []
    
    for species_name in species_of_interest:
        matching_categories = list(filter(lambda x: x['name'] == species_name, categories))
        if len(matching_categories) == 0:
            continue
        assert len(matching_categories) == 1
        category = matching_categories[0]
        category_id = category['id']
        category_ids.append(category_id)
    
    print('Found {} matching categories for data set {}:'.format(len(category_ids),ds_name))
    
    if len(category_ids) == 0:
        continue
    
    for i_category,category_id in enumerate(category_ids):
        print(category_id_to_name[category_id],end='')
        if i_category != len(category_ids) -1:
            print(',',end='')
    print('')
    
    # Retrieve all the images that match that category
    image_ids_of_interest = {}
    for cat in category_ids:
        image_ids_of_interest[category_id_to_name[cat]] = set([ann['image_id'] for ann in annotations if ann['category_id'] == cat])
    
    # print('Selected {} of {} images for dataset {}'.format(len(image_ids_of_interest),len(images),ds_name))
    
    # Retrieve image file names
    filenames = {}
    for cat in category_ids:
        cat_name = category_id_to_name[cat]
        filenames[cat_name] = [im['file_name'] for im in images if im['id'] in image_ids_of_interest[cat_name]]
        assert len(filenames[cat_name]) == len(image_ids_of_interest[cat_name])
    
    # Convert to URLs
    for cat in category_ids:
        cat_name = category_id_to_name[cat]
        urls_to_download[cat_name] = []
        for fn in filenames[cat_name]:        
            url = base_url + '/' + fn
            urls_to_download[cat_name].append(url)
    
    # Need to make urls_to_download a dictionary --> key:species name, value: list of urls to download

    downloads_by_dataset[ds_name] = {'sas_url':sas_url,'filenames':filenames}
    
# ...for each dataset

for cat in category_ids:
    cat_name = category_id_to_name[cat]
    print('Found {} images to download for category: {}'.format(len(urls_to_download[cat_name]), cat_name))


# Download those image files

if use_azcopy_for_download:
    
    for ds_name in downloads_by_dataset:
    
        print('Downloading images for {} with azcopy'.format(ds_name))
        sas_url = downloads_by_dataset[ds_name]['sas_url']
        filenames = downloads_by_dataset[ds_name]['filenames']
    
        # We want to use the whole relative path for this script (relative to the base of the container)
        # to build the output filename, to make sure that different data sets end up in different folders.
        base_url = sas_url.split('?')[0]
        sas_token = sas_url.split('?')[1]
        
        p = urlparse(base_url)
        account_path = p.scheme + '://' + p.netloc
        assert account_path == 'https://lilablobssc.blob.core.windows.net'
        
        container_and_folder = p.path[1:]
        
        container_name = container_and_folder.split('/')[0]
        folder = container_and_folder.split('/',1)[1]
        
        container_sas_url = account_path + '/' + container_name + '?' + sas_token
        
        # The container name will be included because it's part of the file name
        container_output_dir = output_dir # os.path.join(output_dir,container_name)
        os.makedirs(container_output_dir,exist_ok=True)
        
        filenames = [folder + '/' + s for s in filenames]
    
        # Write out a list of files, and use the azcopy "list-of-files" option to download those files
        # this azcopy feature is unofficially documented at https://github.com/Azure/azure-storage-azcopy/wiki/Listing-specific-files-to-transfer
        az_filename = os.path.join(output_dir, 'filenames_{}.txt'.format(ds_name.lower().replace(' ','_')))
        with open(az_filename, 'w') as f:
            for fn in filenames:
                f.write(fn.replace('\\','/') + '\n')
                
        cmd = 'azcopy cp "{0}" "{1}" --list-of-files "{2}"'.format(
                container_sas_url, container_output_dir, az_filename)            
        
        # import clipboard; clipboard.copy(cmd)
        
        os.system(cmd)
    
else:
    
    # Loop over files
    print('Downloading images for {0} without azcopy'.format(species_of_interest))
    
    if n_download_threads <= 1:
        for cat in category_ids:
            cat_name = category_id_to_name[cat]
            print('Downloading images for {0} without azcopy'.format(cat_name))
            for url in tqdm(urls_to_download[cat_name]):        
                download_relative_filename(url, output_dir, cat_name, verbose=True)
        
    else:
    
        pool = ThreadPool(n_download_threads)        
        tqdm(pool.imap(lambda s: download_relative_filename(s,output_dir,verbose=False), urls_to_download), total=len(urls_to_download))
    
print('Done!')