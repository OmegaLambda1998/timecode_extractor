import cv2
import argparse
from skimage.metrics import structural_similarity as ssim

digit_images = [cv2.imread(f'digits/{i}.jpg', cv2.IMREAD_GRAYSCALE) for i in range(10)]

"""
    get_frame_at_time(video_path, target_time)

Returns a frame from a video at a given time.

# Arguments
- `video_path`: Path to the video file.
- `target_time`: Time in seconds to get the frame from.
"""
def get_frame_at_time(video_path, target_time):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    target_frame = round(target_time * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    ret, frame = cap.read()
    cap.release()
    return frame

"""
    extract_timecode_image(frame, source="Nat Geo")

Returns the timecode image from a frame.

# Arguments
- `frame`: Frame to extract the timecode image from.
- `source`: Source of the video. Currently only supports "Nat Geo".
"""
def extract_timecode_image(frame, source="Nat Geo"):
    if source == "Nat Geo":
        timecode_image = extract_nat_geo_timecode_image(frame)
    else:
        print(f"Unknown source: {source}, possible options are 'Nat Geo'")
        timecode_image = None
    return timecode_image

"""
    split_nat_geo_timecode_image(timecode_image)

Returns the timecode image from a Nat Geo frame.

# Arguments
- `timecode_image`: Timecode image to split.
"""
def extract_nat_geo_timecode_image(frame):
    height = frame.shape[0]
    width = frame.shape[1]
    x_min = round(width * 0.3905)
    x_max = round(width * 0.61)
    y_min = round(height * 0.807)
    y_max = round(height * 0.865)
    timecode_image = frame[y_min:y_max, x_min:x_max]
    return timecode_image

"""
    split_timecode_image(timecode_image, source="Nat Geo") 

Split the timecode image into individual digits.

# Arguments
- `timecode_image`: Timecode image to split.
"""
def split_timecode_image(timecode_image, source="Nat Geo"):
    if source == "Nat Geo":
        timecode_digits = split_nat_geo_timecode_image(timecode_image)
    else:
        print(f"Unknown source: {source}, possible options are 'Nat Geo'")
        timecode_digits = None
    return timecode_digits

"""
    split_nat_geo_timecode_image(timecode_image)

Split a Nat Geo timecode image into individual digits.

# Arguments
- `timecode_image`: Timecode image to split.
"""
def split_nat_geo_timecode_image(timecode_image):
    height = timecode_image.shape[0]
    width = timecode_image.shape[1]
    digit_width = round(width * 0.095)
    big_jump = round(width * 0.0618)
    small_jump = round(width * 0.0119)
    jumps = [small_jump, big_jump, small_jump, big_jump, small_jump, big_jump, small_jump, big_jump]
    digit_height = height
    timecode_digits = []
    x_min = 0
    for i in range(8):
        x_max = x_min + digit_width
        y_min = 0
        y_max = digit_height
        digit = timecode_image[y_min:y_max, x_min:x_max]
        timecode_digits.append(digit)
        x_min = x_max + jumps[i]
    return timecode_digits

"""
    pad_image_to_match_dimensions(image_to_pad, reference_image)

Pad an image with white to match the dimensions of a reference image.

# Arguments
- `image_to_pad`: Image to pad.
- `reference_image`: Image to match dimensions with.
"""
def pad_image_to_match_dimensions(image_to_pad, reference_image):
    # Get the dimensions of the reference image
    reference_height, reference_width = reference_image.shape[:2]

    # Get the dimensions of the image to be padded
    original_height, original_width = image_to_pad.shape[:2]

    # Calculate the amount of padding needed on each side
    pad_top = (reference_height - original_height) // 2
    pad_bottom = reference_height - original_height - pad_top
    pad_left = (reference_width - original_width) // 2
    pad_right = reference_width - original_width - pad_left

    # Pad the image with white
    padded_image = cv2.copyMakeBorder(image_to_pad, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=255)

    return padded_image

"""
    read_digit_from_image(digit_image, i)

Read a digit from an image.

# Arguments
- `digit_image`: Image of the digit to read.
- `i`: Index of the digit.
"""
def read_digit_from_image(digit_image):
    gray = cv2.cvtColor(digit_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    digits = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7:0, 8:0, 9:0}
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        roi = thresh[y:y + h, x:x + w]
        for (i, digit_image) in enumerate(digit_images):
            roi = pad_image_to_match_dimensions(roi, digit_image)
            similarity_index, _ = ssim(roi, digit_image, full=True)
            if similarity_index > digits[i]:
                digits[i] = similarity_index
    return max(digits, key=digits.get)

"""
    timecode_to_seconds(timecode)

Convert a timecode to seconds.

# Arguments
- `timecode`: Timecode to convert.
"""
def timecode_to_seconds(timecode):
    time = timecode.split(":")
    hours = int(time[0])
    minutes = int(time[1])
    seconds = int(time[2])
    frame = int(time[3])
    return hours * 3600 + minutes * 60 + seconds + frame / 25

"""
    read_input_csv(input_path)

Read an input CSV file.

# Arguments
- `input_path`: Path to the input CSV file.
"""
def read_input_csv(input_path):
    with open(input_path, "r") as input_file:
        raw_lines = input_file.readlines()
    header = raw_lines[0].split(",")
    rows = [line.split(",") for line in raw_lines[1:]][:-1]
    input_csv = {header[i].strip(): [row[i].strip() for row in rows] for i in range(len(header))}
    return input_csv

"""
    get_args()

Get the command line arguments.
"""
def get_args():
    parser = argparse.ArgumentParser(description="Extract timecode from a video.")
    cl_group = parser.add_argument_group("Command Line Arguments", "Extract timecodes from within the terminal.")
    cl_group.add_argument("-v", "--video", type=str, required=False, help="Path to the video file.")
    cl_group.add_argument("-t", "--time", type=str, required=False, nargs="*", help="Timecode to extract in the format HH:MM:SS:frame.")
    csv_group = parser.add_argument_group("CSV Arguments", "Extract timecodes from a CSV file.")
    csv_group.add_argument("-i", "--input", type=str, required=False, help="Path to the CSV file.")
    csv_group.add_argument("-o", "--output", type=str, required=False, help="Output path for the CSV file.")
    return parser.parse_args()

"""
    main(args)

Main function.

# Arguments
- `args`: Command line arguments.
"""
def main(args):
    if args.input:
        input_csv = read_input_csv(args.input)
        video_paths = input_csv["Sequence Name"]
        target_times_in = [timecode_to_seconds(time) for time in input_csv["Sequence In"]]
        target_times_out = [timecode_to_seconds(time) for time in input_csv["Sequence Out"]]
        output_csv = input_csv 
        output_csv["Source In"] = []
        output_csv["Source Out"] = []
        for (i, video_path) in enumerate(video_paths):
            print(f"Extracting timecode at input timecode {input_csv['Sequence In'][i]}")
            print(f"Extracting timecode at output timecode {input_csv['Sequence Out'][i]}")
            source_reel = input_csv["Source Reel Name"][i]
            frame_in = get_frame_at_time(video_path, target_times_in[i])
            frame_out = get_frame_at_time(video_path, target_times_out[i])
            timecode_image_in = extract_timecode_image(frame_in, source_reel)
            timecode_image_out = extract_timecode_image(frame_out, source_reel)
            timecode_digits_in = split_timecode_image(timecode_image_in, source_reel)
            timecode_digits_out = split_timecode_image(timecode_image_out, source_reel)
            if timecode_digits_in is not None:
                digits_in = [read_digit_from_image(digit_image) for digit_image in timecode_digits_in]
                print(f"Timecode at input timecode: {digits_in[0]}{digits_in[1]}:{digits_in[2]}{digits_in[3]}:{digits_in[4]}{digits_in[5]}:{digits_in[6]}{digits_in[7]}")
                output_csv["Source In"].append(f"{digits_in[0]}{digits_in[1]}:{digits_in[2]}{digits_in[3]}:{digits_in[4]}{digits_in[5]}:{digits_in[6]}{digits_in[7]}")
            if timecode_digits_out is not None:
                digits_out = [read_digit_from_image(digit_image) for digit_image in timecode_digits_out]
                print(f"Timecode at output timecode: {digits_out[0]}{digits_out[1]}:{digits_out[2]}{digits_out[3]}:{digits_out[4]}{digits_out[5]}:{digits_out[6]}{digits_out[7]}")
                output_csv["Source Out"].append(f"{digits_out[0]}{digits_out[1]}:{digits_out[2]}{digits_out[3]}:{digits_out[4]}{digits_out[5]}:{digits_out[6]}{digits_out[7]}")
        output_txt = ""
        output_txt += f"{', '.join(output_csv.keys())}\n"
        for i in range(len(output_csv["Source In"])):
            for key in output_csv.keys():   
                output_txt += f"{output_csv[key][i]}, "
            output_txt = output_txt[:-2]
            output_txt += "\n"
        with open(args.output, "w") as output_file:
            output_file.write(output_txt)
    else:
        video_path = args.video 
        target_times = [timecode_to_seconds(time) for time in args.time]
        for (t, target_time) in enumerate(target_times):
            print(f"Extracting timecode at input timecode {args.time[t]}")
            frame = get_frame_at_time(video_path, target_time)
            timecode_image = extract_timecode_image(frame)
            timecode_digits = split_timecode_image(timecode_image)
            digits = []
            for i in range(len(timecode_digits)):
                digit_image = timecode_digits[i]
                digit = read_digit_from_image(digit_image)
                digits.append(digit)
            print(f"Timecode at input timecode {t}: {digits[0]}{digits[1]}:{digits[2]}{digits[3]}:{digits[4]}{digits[5]}:{digits[6]}{digits[7]}")

if __name__ == "__main__":
    args = get_args()
    main(args)
