import os
import datetime
import pathlib
import glob
import ntpath
import argparse
import exif
import imghdr
import re


def get_datetime_from_metadata(photo_path):
    metadata_tags = ['datetime_original', 'datetime']
    for tag in metadata_tags:
        try:
            with open(photo_path, 'rb') as image_file:
                date_taken_string = exif.Image(image_file).get(tag)
                return datetime.datetime.strptime(date_taken_string, '%Y:%m:%d %H:%M:%S')
        except:
            continue
    return None


def get_datetime_from_filename(photo_path):
    filenames_patterns = {'(January|February|March|April|May|June|July|August|September|October|November|December) ([0-3][0-9]), ((?<!\d)\d{4}(?!\d)) at (((1[0-2]|0?[1-9])([0-5][0-9]) ?([AaPp][Mm])))': '%B %d, %Y at %I%M%p',
                           '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) ([0-3][0-9]), ((?<!\d)\d{4}(?!\d)) at (((1[0-2]|0?[1-9])([0-5][0-9]) ?([AaPp][Mm])))': '%b %d, %Y at %I%M%p',
                           '[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])-([0-2][0-9]h[0-5][0-9]m[0-5][0-9]s)': '%Y-%m-%d-%Hh%Mm%Ss',
                           '([0-9]{4}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])-([0-2][0-9]h[0-5][0-9]m[0-5][0-9]s))': '%Y%m%d-%Hh%Mm%Ss',
                           '([0-9]{4}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1]) ([0-2][0-9]h[0-5][0-9]m[0-5][0-9]s))': '%Y%m%d %Hh%Mm%Ss',
                           'IMG_[0-9]{4}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])_(([0-2][0-9])([0-5][0-9])([0-5][0-9]))': 'IMG_%Y%m%d_%H%M%S',
                           'Screenshot_[0-9]{4}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])-(([0-2][0-9])([0-5][0-9])([0-5][0-9]))': 'Screenshot_%Y%m%d-%H%M%S',
                           'IMG-[0-9]{4}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])-': 'IMG-%Y%m%d-'}

    for pattern in filenames_patterns:
        try:
            filename = ntpath.basename(photo_path)
            x = re.search(pattern, filename)
            return datetime.datetime.strptime(x.group(), filenames_patterns.get(pattern))
        except:
            continue

    return None


def move_photo(photo_path, target_directory, datetime_object):
    while True:
        target_path = target_directory + "/" + datetime_object.strftime('%Y/%m/%Y-%m-%d %Hh%Mm%Ss') + pathlib.Path(photo_path).suffix
        if not os.path.isfile(target_path):
            break
        datetime_object += datetime.timedelta(seconds=1)
    print("Moving to: " + target_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    os.replace(photo_path, target_path)


def sort_photos(source_directory, target_directory, raise_exception=False):
    total = 0
    matched = 0

    directory_contents = list(glob.iglob(source_directory + '/**/*', recursive=True))
    for item in directory_contents:

        if os.path.isfile(item):

            is_image = imghdr.what(item)
            if is_image:
                total += 1

                print("Processing: " + item)

                date_from_metadata = get_datetime_from_metadata(item)
                if date_from_metadata:
                    move_photo(item, target_directory, date_from_metadata)
                    matched += 1
                    continue

                date_from_filename = get_datetime_from_filename(item)
                if date_from_filename:
                    move_photo(item, target_directory, date_from_filename)
                    matched += 1
                    continue

    print("Total: " + str(total))
    print("Matched: " + str(matched))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('source', help='location of the folder with all your photos')
    parser.add_argument('target', help='where you want the photos moved to')
    args = parser.parse_args()

    if not sort_photos(args.source, args.target):
        exit(1)
