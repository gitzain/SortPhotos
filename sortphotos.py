import os
import datetime
import pathlib
import glob
import ntpath
import argparse
import exif
import imghdr


def get_image_files(directory):
    all_files_in_directory = list(glob.iglob(directory + '/**/*', recursive=True))

    images_in_directory = []
    for file_path in all_files_in_directory:
        if imghdr.what(file_path):
            images_in_directory.append(file_path)

    return images_in_directory


def fix_image_extentions(images_array):
    for image_path in images_array:
        image_extention = imghdr.what(image_path)
        if image_extention:
            if image_extention not in pathlib.Path(image_path).suffix:
                print("Fixing extention of " + image_path)
                thisFile = pathlib.Path(image_path)
                target = thisFile.with_suffix('.' + image_extention)
                if not os.path.isfile(target):
                    thisFile.rename(target)


def get_metadata_tag(photo_path, tag):
    try:
        with open(photo_path, 'rb') as image_file:
            return exif.Image(image_file).get(tag)
    except:
        return None


def get_datetime_from_metadata(photo_path):
    metadata_tags = ['datetime_original', 'datetime']
    for tag in metadata_tags:
        date_taken_string = get_metadata_tag(photo_path, tag)
        if date_taken_string:
            print('Data taken string: ' + date_taken_string)
            return datetime.datetime.strptime(date_taken_string, '%Y:%m:%d %H:%M:%S')
    return None


def get_datetime_from_filename(photo_path):
    filename_patterns = ['%Y%m%d-%Hh%Mm%Ss', '%B %d, %Y at %I%M%p', 'IMG-%Y%m%d-WA%H%M', 'Screenshot_%Y%m%d-%H%M%S']
    output = None
    for pattern in filename_patterns:
        filename = ntpath.basename(photo_path)
        filename = os.path.splitext(filename)[0]
        try:
            output = datetime.datetime.strptime(filename, pattern)
            return output
        except:
            continue
    return output


def move_photo(photo_path, target_directory, datetime_object):
    target_path = target_directory + "/" + datetime_object.strftime('%Y/%m/%Y-%m-%d %Hh%Mm%Ss') + pathlib.Path(photo_path).suffix
    while os.path.isfile(target_path):
        new_datetime = datetime_object + 1
        target_path = target_directory + "/" + new_datetime.strftime('%Y/%m/%Y-%m-%d %Hh%Mm%Ss') + pathlib.Path(photo_path).suffix
    print("Moving to: " + target_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    os.replace(photo_path, target_path)


def sort_photos(source_directory, target_directory, raise_exception=False):
    total = len(get_image_files(source_directory))
    matched = 0

    for image in get_image_files(source_directory):
        print("**********")
        print("Processing: " + image)

        date_from_metadata = get_datetime_from_metadata(image)
        if date_from_metadata:
            move_photo(image, target_directory, date_from_metadata)
            matched += 1
            continue

        date_from_filename = get_datetime_from_filename(image)
        if date_from_filename:
            move_photo(image, target_directory, date_from_filename)
            matched += 1
            continue

    print("Total: " + str(total))
    print("Matched: " + str(matched))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('source', help='location of the folder with all your photos')
    parser.add_argument('target', help='where you want the photos moved to')
    parser.add_argument('--fix_extentions', help='this will correct file extentions of images in the source directory')
    args = parser.parse_args()

    if args.fix_extentions is not None:
        fix_image_extentions(get_image_files(args.source))

    if not sort_photos(args.source, args.target):
        exit(1)
