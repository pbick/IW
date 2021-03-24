#
# Quick script to merge the photos of male and female lions into one "lion" folder
#

import os

dataset = "test"

print("Merging lions for", dataset)

male_filenames = os.listdir(f"Datasets/{dataset}/lionmale")
print("Num male images:", len(male_filenames))
female_filenames = os.listdir(f"Datasets/{dataset}/lionfemale")
print("Num female images:", len(female_filenames))

new_dir = "lion"

os.makedirs(f"Datasets/{dataset}/{new_dir}",exist_ok=True)

for fn in female_filenames:
    os.rename(f"Datasets/{dataset}/lionfemale/{fn}", f"Datasets/{dataset}/{new_dir}/{fn}")

count = 0
for fn in male_filenames:
    if fn not in female_filenames:
        os.rename(f"Datasets/{dataset}/lionmale/{fn}", f"Datasets/{dataset}/{new_dir}/{fn}")
    else:
        count += 1

combined_filenames = os.listdir(f"Datasets/{dataset}/{new_dir}")
print("Num combined images:", len(combined_filenames))
print("Num duplicates:", count)