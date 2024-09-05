# import os
# import time
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import cv2
# import numpy as np
# from PIL import Image
# from io import BytesIO
# import base64
# import threading
# from queue import Queue

# # Set up the path to chromedriver in the current directory
# chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')

# # Set up ChromeDriver using the Service class
# service = Service(executable_path=chromedriver_path)
# driver = webdriver.Chrome(service=service)

# # Navigate to Oculus casting page
# driver.get('https://www.oculus.com/casting')

# # Function to wait for login to be completed
# def wait_for_login(driver, video_tag, timeout=300):
#     try:
#         WebDriverWait(driver, timeout).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, video_tag))
#         )
#         print("Login completed and video element is detected.")
#     except Exception as e:
#         print("Login not completed or video element not found within the time limit.")
#         driver.quit()
#         raise e

# # Function to capture a frame
# def capture_frame(video_element):
#     js_code = """
#         var canvas = document.createElement('canvas');
#         var video = arguments[0];

#         if (video.readyState >= 2 && video.currentTime > 0) {
#             canvas.width = video.videoWidth;
#             canvas.height = video.videoHeight;
#             canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
#             return canvas.toDataURL('image/png');
#         } else {
#             return null;
#         }
#     """
#     frame = driver.execute_script(js_code, video_element)
    
#     if frame is None:
#         time.sleep(2)
#         frame = driver.execute_script(js_code, video_element)
#         if frame is None:
#             raise ValueError("Failed to capture frame: video is not fully loaded or canvas is empty after retry.")
    
#     base64_data = frame.split(',')[1] if ',' in frame else frame

#     try:
#         image = Image.open(BytesIO(base64.b64decode(base64_data)))
#         img_np = np.array(image)
#         img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
#         return img_bgr
#     except Exception as e:
#         raise ValueError(f"Error processing the image frame: {e}")

# # Function to check if the video element exists
# def check_video_element(video_tag):
#     video_elements = driver.find_elements(By.CSS_SELECTOR, video_tag)
#     return video_elements[0] if len(video_elements) > 0 else None

# # Function to save a frame as JPEG asynchronously
# def save_frame_async(queue):
#     while True:
#         img, folder_path, frame_count = queue.get()
#         file_name = f"frame_{frame_count}.jpg"
#         file_path = os.path.join(folder_path, file_name)
#         cv2.imwrite(file_path, img)
#         print(f"Frame {frame_count} saved as {file_name}")
#         queue.task_done()

# # Create directory structure for saving frames
# def create_save_directory():
#     base_dir = os.path.join(os.getcwd(), 'PassThroughFrames')
#     if not os.path.exists(base_dir):
#         os.makedirs(base_dir)
#     timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
#     session_dir = os.path.join(base_dir, timestamp)
#     os.makedirs(session_dir)
#     return session_dir

# # Video tag selector
# video_tag = 'video.xh8yej3.xt7dq6l.x186iv6y'

# # Wait for login to be completed and video element to appear
# wait_for_login(driver, video_tag)

# # Find the video element once it's present
# video_element = check_video_element(video_tag)

# # Start an async saving queue and worker threads
# save_queue = Queue()
# threading.Thread(target=save_frame_async, args=(save_queue,), daemon=True).start()

# # Capture frames if the video exists
# if video_element:
#     print("Video element found. Starting frame capture.")
    
#     # Start time measurement
#     start_time = time.time()
    
#     save_directory = create_save_directory()
#     frame_count = 0
#     try:
#         while True:
#             frame = capture_frame(video_element)
            
#             # Add the frame to the queue for saving
#             save_queue.put((frame, save_directory, frame_count))
            
#             # Display the captured frame
#             cv2.imshow("Captured Frame", frame)

#             frame_count += 1

#             # Press 'q' to exit the capture loop
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 print("Exiting frame capture.")
#                 break

#             # Limit to 60 FPS
#             time.sleep(1 / 60)

#     finally:
#         cv2.destroyAllWindows()
# else:
#     print("No video element found.")

# # Close the browser
# driver.quit()

# # Wait for all frames to be saved
# save_queue.join()

# # End time measurement
# end_time = time.time()

# # Print the total time taken
# total_time = end_time - start_time

# print(f"Total time for capturing and saving frames: {total_time:.2f} seconds")

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
import threading
from queue import Queue, Empty

# Set up the path to chromedriver in the current directory
chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')

# Set up ChromeDriver using the Service class
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service)

# Navigate to Oculus casting page
driver.get('https://www.oculus.com/casting')

# Global flag to indicate capture stop
stop_capture = False

# Function to wait for login to be completed
def wait_for_login(driver, video_tag, timeout=300):
    try:
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
    js_code = """
        var canvas = document.createElement('canvas');
        var video = arguments[0];

        if (video.readyState >= 2 && video.currentTime > 0) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
            return canvas.toDataURL('image/png');
        } else {
            return null;
        }
    """
    frame = driver.execute_script(js_code, video_element)
    
    if frame is None:
        time.sleep(2)
        frame = driver.execute_script(js_code, video_element)
        if frame is None:
            raise ValueError("Failed to capture frame: video is not fully loaded or canvas is empty after retry.")
    
    base64_data = frame.split(',')[1] if ',' in frame else frame

    try:
        image = Image.open(BytesIO(base64.b64decode(base64_data)))
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        return img_bgr
    except Exception as e:
        raise ValueError(f"Error processing the image frame: {e}")

# Function to check if the video element exists
def check_video_element(video_tag):
    video_elements = driver.find_elements(By.CSS_SELECTOR, video_tag)
    return video_elements[0] if len(video_elements) > 0 else None

# Function to save a frame as JPEG asynchronously
def save_frame_async(queue):
    while True:
        try:
            img, folder_path, frame_count = queue.get(timeout=1)
            file_name = f"frame_{frame_count}.jpg"
            file_path = os.path.join(folder_path, file_name)
            cv2.imwrite(file_path, img)
            print(f"Frame {frame_count} saved as {file_name}")
            queue.task_done()
        except Empty:
            if stop_capture:
                break

# Create directory structure for saving frames
def create_save_directory():
    base_dir = os.path.join(os.getcwd(), 'PassThroughFrames')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    session_dir = os.path.join(base_dir, timestamp)
    os.makedirs(session_dir)
    return session_dir

# Video tag selector
video_tag = 'video.xh8yej3.xt7dq6l.x186iv6y'

# Wait for login to be completed and video element to appear
wait_for_login(driver, video_tag)

# Find the video element once it's present
video_element = check_video_element(video_tag)

# Start an async saving queue and worker threads
save_queue = Queue()
threading.Thread(target=save_frame_async, args=(save_queue,), daemon=True).start()

# Capture frames if the video exists
if video_element:
    print("Video element found. Starting frame capture.")
    
    # Start time measurement
    start_time = time.time()
    
    save_directory = create_save_directory()
    frame_count = 0
    try:
        while True:
            frame = capture_frame(video_element)
            
            # Add the frame to the queue for saving
            save_queue.put((frame, save_directory, frame_count))
            
            # Display the captured frame
            cv2.imshow("Captured Frame", frame)

            frame_count += 1

            # Press 'q' to exit the capture loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting frame capture.")
                global stop_capture  # Declare global inside the loop where it's used
                stop_capture = True  # Set stop flag
                break

            # Limit to 60 FPS
            time.sleep(1 / 60)

    finally:
        cv2.destroyAllWindows()
else:
    print("No video element found.")

# Close the browser
driver.quit()

# Wait for all frames to be saved or timeout quickly
save_queue.join()

# End time measurement
end_time = time.time()

# Print the total time taken
total_time = end_time - start_time
print(f"Total time for capturing and saving frames: {total_time:.2f} seconds")
