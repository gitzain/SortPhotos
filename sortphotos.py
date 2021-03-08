import argparse, os, datetime, imghdr, pathlib, exif

def get_all_files(directory):
    files_in_directory = []

    for root, directories, files in os.walk(directory):
        for item in files:
            files_in_directory.append(os.path.join(root, item))

    return files_in_directory


def get_image_files(directory):
    images_in_directory = []

    for file_path in get_all_files(directory):
        if imghdr.what(file_path):
            images_in_directory.append(file_path)
    
    return images_in_directory


def fix_image_extentions(images_array):
    for image_path in images_array:
        image_extention = imghdr.what(image_path)
        if image_extention:
            thisFile = pathlib.Path(image_path)
            thisFile.rename(thisFile.with_suffix('.' + image_extention))


def get_metadata_tag(photo_path, tag):
    try:
        with open(photo_path, 'rb') as image_file:
            return exif.Image(image_file).get(tag)
    except:
        return None


def sort_photos(source_directory, target_directory, raise_exception=False):
    for image in get_image_files(source_directory):
        date_taken_string = get_metadata_tag(image, 'datetime_original')
        if date_taken_string:
            print("**********")
            print("Processing: " + image)
            date_take_object = datetime.datetime.strptime(date_taken_string, '%Y:%m:%d %H:%M:%S')
            target_path = target_directory + "/" + date_take_object.strftime('%Y/%m/%Y-%m-%d %Hh%Mm%Ss') + pathlib.Path(image).suffix
            print("Moving to: " + target_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            os.replace(image, target_path)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('source', help='location of the folder with all your photos')
    parser.add_argument('target', help='where you want the photos moved to')
    parser.add_argument('--fix_extentions', help='this will correct file extentions of images in the source directory')
    args = parser.parse_args()

    if args.fix_extentions is not None:
        fix_image_extentions(get_all_files(args.source))

    if not sort_photos(args.source, args.target):
        exit(1)