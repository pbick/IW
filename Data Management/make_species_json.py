import numpy as np 
import json

# Helper method
def get_id_from_name(name):
    for cat in data_all['categories']:
        if cat['name'] == name:
            return cat['id']

# Script starts here
with open('Downloads/SnapshotSerengetiS01.json') as f:
    data_s1 = json.load(f)
print("Total # of season 1 images:", len(data_s1['images']))

with open('Downloads/SnapshotSerengeti_S1-11_v2.1.json') as f:
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

big_json = {}

for name, s1 in species:
    if s1:
        data = data_s1
    else:
        data = data_all
    
    species_id = get_id_from_name(name)
    im_ids = [annotation["image_id"] for annotation in data['annotations'] if annotation['category_id'] == species_id]
    images = [image for image in data['images'] if image['id'] in im_ids]

    big_json[name] = images

print("Finished creating dictionary, now printing image counts")
for name in big_json:
    print(f"Species: {name} | Images found: {len(big_json[name])}")

with open("species_images.json", "w") as outfile:
    json.dump(big_json, outfile)