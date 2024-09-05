import os
import sys
import cv2

def make_video_from_frames(input_directory, output_directory, frame_rate=30):
    # Get the full path of the input directory under PassThroughFrames
    input_directory = os.path.join("PassThroughFrames", input_directory)

    # Get the list of JPEG image files in the directory, sorted by their names
    images = sorted([img for img in os.listdir(input_directory) if img.endswith(".jpg") or img.endswith(".jpeg")],
                    key=lambda x: int(x.replace('frame_', '').replace('.jpg', '').replace('.jpeg', '')))

    if not images:
        print("No images found in the directory.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Set the output video filename using the directory name
    video_filename = os.path.join(output_directory, os.path.basename(input_directory) + '.mp4')

    # Load the first image to get the video properties
    first_frame_path = os.path.join(input_directory, images[0])
    frame = cv2.imread(first_frame_path)
    height, width, layers = frame.shape

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
    video = cv2.VideoWriter(video_filename, fourcc, frame_rate, (width, height))

    for image in images:
        img_path = os.path.join(input_directory, image)
        img_frame = cv2.imread(img_path)

        if img_frame is None:
            print(f"Warning: Skipping {img_path}, could not be read.")
            continue

        video.write(img_frame)

    video.release()
    print(f"Video saved as {video_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python image_to_video.py <input_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]

    # Ensure the input directory exists under PassThroughFrames
    full_input_dir = os.path.join("PassThroughFrames", input_dir)
    if not os.path.exists(full_input_dir):
        print(f"Error: Directory {full_input_dir} does not exist.")
        sys.exit(1)

    # Set the output directory for saving the video
    output_dir = os.path.join(os.getcwd(), 'PassThroughVideos')

    # Make the video from the frames in the input directory with 60fps
    make_video_from_frames(input_dir, output_dir, frame_rate=60)