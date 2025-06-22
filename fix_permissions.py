import os
import shutil
import stat

def fix_permissions():
    """
    Script to fix file permissions on Windows
    Run this script to fix the permission issues
    """
    vectorstore_path = r"D:\cosmic_soul_intern_task_application\vectorstores"
    
    if not os.path.exists(vectorstore_path):
        print(f"Path doesn't exist: {vectorstore_path}")
        return
    
    print(f"Fixing permissions for: {vectorstore_path}")
    
    try:
        # Method 1: Change file permissions
        for root, dirs, files in os.walk(vectorstore_path):
            # Fix directory permissions
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    os.chmod(dir_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    print(f"Fixed directory permissions: {dir_path}")
                except Exception as e:
                    print(f"Could not fix directory {dir_path}: {e}")
            
            # Fix file permissions
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
                    print(f"Fixed file permissions: {file_path}")
                except Exception as e:
                    print(f"Could not fix file {file_path}: {e}")
        
        print("✅ Permission fix completed!")
        
    except Exception as e:
        print(f"❌ Error fixing permissions: {e}")
        
        # Method 2: Copy to new location if permission fix fails
        print("Trying to copy files to a new location...")
        try:
            new_path = os.path.join(os.path.expanduser("~"), "Documents", "vectorstores_backup")
            if os.path.exists(new_path):
                shutil.rmtree(new_path)
            shutil.copytree(vectorstore_path, new_path)
            print(f"✅ Files copied to: {new_path}")
            print("You can now update your VECTORSTORE_BASE path to use this location")
        except Exception as copy_error:
            print(f"❌ Copy also failed: {copy_error}")

if __name__ == "__main__":
    fix_permissions()