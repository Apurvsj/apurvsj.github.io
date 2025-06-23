import os
import shutil

SOURCE_DIR = "seo-blog"
TARGET_DIR = "."

def move_files_to_root():
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Folder '{SOURCE_DIR}' does not exist.")
        return

    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), SOURCE_DIR)
            target_path = os.path.join(TARGET_DIR, rel_path)

            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.move(os.path.join(root, file), target_path)
            print(f"✅ Moved: {rel_path}")

    # Remove empty folders
    shutil.rmtree(SOURCE_DIR)
    print(f"🧹 Removed folder: {SOURCE_DIR}")

    print("\n🚀 Project moved to root! Now commit and push your changes:\n")
    print("    git add .")
    print("    git commit -m \"Move SEO blog to root for GitHub Pages + AdSense\"")
    print("    git push")

if __name__ == "__main__":
    move_files_to_root()
