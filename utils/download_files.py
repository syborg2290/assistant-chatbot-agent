import os
import requests


def download_file(url, download_dir="agent/tmp"):
    try:
        # Create the directory if it doesn't exist
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        response = requests.get(url)
        response.raise_for_status()

        # Get the file extension from the URL (if available)
        extension = os.path.splitext(url)[-1] or ".tmp"

        # Create a temporary file in the specified directory
        file_name = f"temp{extension}"
        temp_path = os.path.join(download_dir, file_name)
        with open(temp_path, "wb") as temp_file:
            temp_file.write(response.content)

        print(f"File downloaded to: {temp_path}")

        # Return the path to the downloaded file
        return file_name

    except requests.RequestException as e:
        print(f"Failed to download file: {e}")
        raise


def cleanup_temp_file(file_path):
    """Delete the temporary file after processing."""
    try:
        os.remove(file_path)
        print(f"Temporary file removed: {file_path}")
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")
        raise


# Example usage
# download_file("https://www.example.com/sample.pdf")
# download_file("https://www.example.com/sample.csv")
# download_file("https://www.example.com/sample.xlsx")
# download_file("https://www.example.com/sample.json")
# download_file("https://www.example.com/sample.txt")
