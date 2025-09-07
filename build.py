import htmlmin
import os

SOURCE_DIR = "frontend"
DEST_DIR = "dist"
SOURCE_FILE = os.path.join(SOURCE_DIR, "index.html")
DEST_FILE = os.path.join(DEST_DIR, "index.html")

def build():
    """
    Reads the source HTML file, minifies its content, and saves the result
    to the distribution directory. This prepares the frontend for production.
    """
    print("Starting build process...")

    # Ensure the destination directory exists. If not, create it.
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        print(f"Created directory: {DEST_DIR}")

    # Read the source HTML file.
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            html_content = f.read()
        print(f"Successfully read source file: {SOURCE_FILE}")
    except FileNotFoundError:
        print(f"Error: Source file not found at {SOURCE_FILE}. Aborting build.")
        return

    # Minify the HTML content, removing comments and extra whitespace.
    minified_content = htmlmin.minify(
        html_content,
        remove_comments=True,
        remove_empty_space=True
    )
    print("HTML content minified successfully.")

    # Write the minified content to the destination file.
    with open(DEST_FILE, "w", encoding="utf-8") as f:
        f.write(minified_content)
    
    print(f"Build successful! Optimized file saved to {DEST_FILE}")

if __name__ == "__main__":
    build()

