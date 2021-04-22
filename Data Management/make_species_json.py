import numpy as np 
import json
import random

# Helper method
def get_id_from_name(name):
    for cat in data['categories']:
        if cat['name'] == name:
            return cat['id']

# Script starts here
with open('skr_files/SnapshotKruger_S1_v1.0.json') as f:
    data_s1 = json.load(f)
print("Total # of season 1 images:", len(data_s1['images']))

# with open('SnapshotSerengeti_S1-11_v2.1.json') as f:
#     data_all = json.load(f)
# print("Total # of images for all seasons:", len(data_all['images']))
# print()
data_all = None

# If boolean is True, only picks images from S1. If False, picks images from all seasons
species = [
    ('leopard', True),
    ('waterbuck', True),
    ('lionmale', True), 
    ('lionfemale', True),
    ('buffalo', True),
    ('elephant', True),
    ('hyenaspotted', True),
    ('empty', True)
]
# species = [('empty', True)]

big_json = {}

for name, s1 in species:
    if s1:
        data = data_s1
    else:
        data = data_all
    
    species_id = get_id_from_name(name)
    print(f"Species: {name}; ID: {species_id}; S1 only? {s1}")
    im_ids = [annotation["image_id"] for annotation in data['annotations'] if annotation['category_id'] == species_id]
    print(f"Found {len(im_ids)} images for species")
    
    # These two lines are only for emptys
    if name == "empty":
        random.shuffle(im_ids)
        im_ids = im_ids[:800]

    images = [image for image in data['images'] if image['id'] in im_ids]
    
    big_json[name] = images

print("Finished creating dictionary, now printing image counts")
for name in big_json:
    print(f"Species: {name} | Images found: {len(big_json[name])}")

json_filename = "skr_files/species_images.json"
with open(json_filename, "w") as outfile:
    json.dump(big_json, outfile, indent=1)