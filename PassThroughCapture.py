import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import base64

# Set up the path to chromedriver in the current directory
chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')

# Set up ChromeDriver using the Service class
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service)

# Navigate to Oculus casting page
driver.get('https://www.oculus.com/casting')

# Function to wait for login to be completed
def wait_for_login(driver, video_tag, timeout=300):
    try:
        # Wait until the page contains the video element or login is completed
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, video_tag))
        )
        print("Login completed and video element is detected.")
    except Exception as e:
        print("Login not completed or video element not found within the time limit.")
        driver.quit()
        raise e

# Function to capture a frame
def capture_frame(video_element):
    # Use JavaScript to ensure the video is playing and capture the frame
    js_code = """
        var canvas = document.createElement('canvas');
        var video = arguments[0];

        // Ensure video is playing by checking the readyState and currentTime
        if (video.readyState >= 2 && video.currentTime > 0) {
            // Set the canvas size to the video resolution
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            // Draw the video frame onto the canvas at full resolution
            canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

            // Return the canvas as a base64-encoded PNG image
            return canvas.toDataURL('image/png');
        } else {
            return null;  // Video is not ready yet
        }
    """
    frame = driver.execute_script(js_code, video_element)

    # Check if the frame is valid
    if frame is None:
        # Try adding a delay and attempt capturing again
        time.sleep(2)  # Add a delay to allow video to start playing
        frame = driver.execute_script(js_code, video_element)
        if frame is None:
            raise ValueError("Failed to capture frame: video is not fully loaded or canvas is empty after retry.")

    # Remove metadata from the base64 string (strip 'data:image/png;base64,')
    base64_data = frame.split(',')[1] if ',' in frame else frame

    try:
        # Decode the base64 data into an image
        image = Image.open(BytesIO(base64.b64decode(base64_data)))
        # Convert the image to a numpy array so it can be processed with OpenCV
        img_np = np.array(image)
        # Convert from RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Print the captured frame's resolution for debugging purposes
        print(f"Captured frame resolution: {img_bgr.shape[1]}x{img_bgr.shape[0]}")

        return img_bgr
    except Exception as e:
        raise ValueError(f"Error processing the image frame: {e}")


# Function to check if the video element exists
def check_video_element(video_tag):
    video_elements = driver.find_elements(By.CSS_SELECTOR, video_tag)
    if len(video_elements) > 0:
        return video_elements[0]  # Return the first video element if found
    else:
        return None

# Function to save a frame as JPEG
def save_frame(img, folder_path, frame_count):
    file_name = f"frame_{frame_count}.jpg"
    file_path = os.path.join(folder_path, file_name)
    cv2.imwrite(file_path, img)
    print(f"Frame {frame_count} saved as {file_name}")

# Create directory structure for saving frames
def create_save_directory():
    base_dir = os.path.join(os.getcwd(), 'PassThroughFrames')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Create a subdirectory based on the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    session_dir = os.path.join(base_dir, timestamp)
    os.makedirs(session_dir)

    return session_dir

# Video tag selector (passed into the functions)
video_tag = 'video.xh8yej3.xt7dq6l.x186iv6y'

# Wait for login to be completed and video element to appear
wait_for_login(driver, video_tag)

# Find the video element once it's present
video_element = check_video_element(video_tag)

# Capture frames only if the video exists
if video_element:
    print("Video element found. Starting frame capture.")

    # Create the directory to save captured frames
    save_directory = create_save_directory()

    # Code to capture frames in a loop
    frame_count = 0
    try:
        while True:  # Continue capturing frames until 'q' is pressed
            frame = capture_frame(video_element)
            save_frame(frame, save_directory, frame_count)
            frame_count += 1

            # Display the captured frame
            cv2.imshow("Captured Frame", frame)

            # Press 'q' to exit the capture loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting frame capture.")
                break

            time.sleep(0.0167)
            # time.sleep(0.1)  # Capture a frame every 1 second
    finally:
        cv2.destroyAllWindows()
else:
    print("No video element found.")

# Close the browser
driver.quit()
