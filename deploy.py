import os
import shutil
import subprocess

# 🔧 Adjust these paths to your actual directories
SOURCE_DIR = r"C:\Users\HP\OneDrive\Desktop\seo_worked"
TARGET_DIR = r"C:\Users\HP\OneDrive\Desktop\apurvsj.github.io"

FILES_TO_COPY = ["index.html", "robots.txt", "sitemap.xml", "ads.txt"]
ARTICLES_FOLDER = "articles"

import stat

def handle_remove_readonly(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)
 
def run_generate():
    print("▶️ Running generate.py...")
    os.system("python generate.py")

def copy_file(file_name):
    src = os.path.join(SOURCE_DIR, file_name)
    dest = os.path.join(TARGET_DIR, file_name)
    if os.path.exists(src):
        shutil.copy2(src, dest)
        print(f"✅ Copied {file_name}")
    else:
        print(f"⚠️ File not found: {file_name}")

def copy_articles():
    src_folder = os.path.join(SOURCE_DIR, ARTICLES_FOLDER)
    dest_folder = os.path.join(TARGET_DIR, ARTICLES_FOLDER)

    if os.path.exists(dest_folder):
        shutil.rmtree(dest_folder, onerror=handle_remove_readonly)
    shutil.copytree(src_folder, dest_folder)
    print("✅ Articles copied.")

def git_push():
    print("📤 Pushing to GitHub...")
    try:
        # Stage changes first
        subprocess.run(["git", "add", "."], cwd=TARGET_DIR, check=True)

        # Commit changes (even if nothing changed, use --allow-empty just in case)
        subprocess.run(["git", "commit", "-m", "🔄 Auto update content", "--allow-empty"], cwd=TARGET_DIR, check=True)

        # Now pull and rebase safely
        subprocess.run(["git", "pull", "--rebase"], cwd=TARGET_DIR, check=True)

        # Finally, push
        subprocess.run(["git", "push"], cwd=TARGET_DIR, check=True)
        print("🚀 Git push successful.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")



if __name__ == "__main__":
    run_generate()
    for file in FILES_TO_COPY:
        copy_file(file)
    copy_articles()
    git_push()
