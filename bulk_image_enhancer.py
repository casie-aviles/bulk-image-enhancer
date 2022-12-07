# import dependencies
from PIL import Image, ImageEnhance
import multiprocessing as mp
import os, os.path
import time
import textwrap
import filecmp

def enhance(source_path, output_path, brightness_factor, sharpness_factor, contrast_factor, start_time, secs, file):

    elapsed_time = time.time() - start_time 

    # check if we haven't reached the time limit (i.e. enhancing time)
    if elapsed_time <= secs:
        # specify acceptable file types/extensions
        img_types = [".jpg",".gif",".png"]

        # get the file extension or file type
        file_type = os.path.splitext(file)[1]
        if file_type.lower() in img_types:  # check if it is acceptable or not
            raw_img = Image.open(os.path.join(source_path, file))   # store as an Image file

            path = os.path.join(output_path, file)  # get the output path + filename

            # adjust brightness of image according to brightness_factor
            brightness_enhancer = ImageEnhance.Brightness(raw_img)
            enhanced_img = brightness_enhancer.enhance(brightness_factor)

            # adjust sharpness of image according to sharpness_factor
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced_img)
            enhanced_img = sharpness_enhancer.enhance(sharpness_factor)

            # adjust contrast of image according to contrast_factor
            contrast_enhancer = ImageEnhance.Contrast(enhanced_img)
            enhanced_img = contrast_enhancer.enhance(contrast_factor)

            # save image to output directory
            enhanced_img.save(path)

            # return a list of pool.ApplyResult object 
            return enhanced_img

def main():

    # ask for user input
    source_path = input("Enter source directory of raw images: ")
    output_path = input("Enter output directory of enhanced images: ")
    
    # source_path = "D:\\Users\\Casie\\Desktop\\bulk-image-enhancer\\cat_photos"
    # output_path = "D:\\Users\\Casie\\Desktop\\bulk-image-enhancer\\output"

    # print('---')
    # print('Factor Notes:')
    # print('Factor == 1 - original image')
    # print('Factor < 1 - darker, lower contrast, lower sharpness')
    # print('Factor > 1 - brighter, higher contrast, sharper')
    # print()

    brightness_factor = float(input("Set brightness factor: "))
    sharpness_factor = float(input("Set sharpness factor: "))
    contrast_factor = float(input("Set contrast factor: "))

    # brightness_factor = float(2)
    # sharpness_factor = float(1)
    # contrast_factor = float(1)
    
    secs = int(float(input("Input enhancing time (minutes): "))*60)

    # store contents of source folder as their string filenames into a list
    dir_contents = os.listdir(source_path)

    enhanced_imgs = []

    # without multiprocessing
    # start_time = time.time()
    # for file in dir_contents:
        # enhanced_imgs.append(enhance(source_path, output_path, brightness_factor, sharpness_factor, contrast_factor, start_time, secs, file))

    # with multiprocessing
    # create a pool of worker processes equivalent to the no. of cores
    pool = mp.Pool(mp.cpu_count())

    start_time = time.time()

    # issue tasks to worker processes using apply_async()
    enhanced_imgs = [pool.apply_async(enhance, args=(source_path, 
                                                    output_path, 
                                                    brightness_factor, 
                                                    sharpness_factor, 
                                                    contrast_factor, 
                                                    start_time, secs, file)) 
                                                    for file in dir_contents]
    
    # shutdown process pool
    pool.close()

    # we're using .get() to retrieve our desired output and have the enhanced images in their output folder
    # this is a step unique to multiprocessing's async functions (e.g. apply_async(), map_async(), etc.)
    for img in enhanced_imgs:
        img.get()

    elapsed_time = round(time.time() - start_time, 2)

    # check how much of the output matches the source images
    output_dir_contents = os.listdir(output_path)

    match = 0

    for file in dir_contents:
        if file in output_dir_contents:
            match+=1

    # write statistics report
    write_text =    f"""
                    Number of images enhanced: {match}
                    Number of raw images: {len(dir_contents)}
                    Output folder: {output_path}
                    Elapsed time: {elapsed_time}
                    Number of pool processes: {mp.cpu_count()}

                    Brightness factor: {brightness_factor}
                    Sharpness factor: {sharpness_factor}
                    Contrast factor: {contrast_factor}
                    """
    text_path = output_path + '\stats.txt'

    with open(text_path, 'w') as f:
        f.write(textwrap.dedent(write_text))

    print("Time elapsed:", elapsed_time, "secs")

if __name__== "__main__" :
    main()
