import numpy as np 
import json
import random

# Helper method
def get_id_from_name(name):
    for cat in data['categories']:
        if cat['name'] == name:
            return cat['id']

# Script starts here
with open('SnapshotSerengetiS01.json') as f:
    data_s1 = json.load(f)
print("Total # of season 1 images:", len(data_s1['images']))

with open('SnapshotSerengeti_S1-11_v2.1.json') as f:
    data_all = json.load(f)
print("Total # of images for all seasons:", len(data_all['images']))
print()

# If boolean is True, only picks images from S1. If False, picks images from all seasons
species = [
    ('leopard', False),
    ('waterbuck', False),
    ('rhinoceros', False),
    ('lionmale', True), 
    ('lionfemale', True),
    ('buffalo', True),
    ('elephant', True),
    ('hyenaspotted', True)
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
    
    # These two lines are only for emptys (comment out)
    # random.shuffle(im_ids)
    # im_ids = im_ids[:3000]

    images = [image for image in data['images'] if image['id'] in im_ids]
    
    big_json[name] = images

print("Finished creating dictionary, now printing image counts")
for name in big_json:
    print(f"Species: {name} | Images found: {len(big_json[name])}")

json_filename = "species_images.json"
with open(json_filename, "w") as outfile:
    json.dump(big_json, outfile)