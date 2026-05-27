import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def convert_py_to_pdf(py_file_path, output_dir="pdf_outputs"):
    # Ensure output folder exists
    os.makedirs(output_dir, exist_ok=True)

    # Create a safe PDF file name to avoid duplicates
    relative_path = py_file_path.replace(":", "").replace("\\", "_").replace("/", "_")
    pdf_file_name = os.path.splitext(os.path.basename(py_file_path))[0] + ".pdf"
    pdf_path = os.path.join(output_dir, pdf_file_name)

    # If filename already exists, make it unique
    counter = 1
    while os.path.exists(pdf_path):
        pdf_file_name = f"{os.path.splitext(os.path.basename(py_file_path))[0]}_{counter}.pdf"
        pdf_path = os.path.join(output_dir, pdf_file_name)
        counter += 1

    # Read .py file with multiple encoding attempts
    code_lines = None
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(py_file_path, 'r', encoding=encoding, errors='ignore') as f:
                code_lines = f.readlines()
                # Check if we got readable text (not binary garbage)
                if code_lines and len(code_lines[0]) > 0 and not any('\x00' in line for line in code_lines[:5]):
                    break
        except Exception:
            continue
    
    if code_lines is None:
        print(f"⚠️ Cannot read file as text (may be compiled/encoded): {py_file_path}")
        return

    # Create PDF file
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    x, y = 50, height - 50
    line_height = 14

    for line in code_lines:
        if y < 50:  # new page if bottom reached
            c.showPage()
            y = height - 50
        c.drawString(x, y, line.rstrip())
        y -= line_height

    c.save()
    print(f"✅ Converted: {py_file_path} → {pdf_path}")


def convert_all_py_recursively(base_dir, output_dir="pdf_outputs"):
    skipped_folders = {'__pycache__', '.git', 'node_modules', '.pytest_cache', '.venv', 'venv'}
    
    for root, dirs, files in os.walk(base_dir):
        # Skip cache and compiled directories
        dirs[:] = [d for d in dirs if d not in skipped_folders and not d.startswith('.')]
        
        for file in files:
            # Only process actual .py source files, skip .pyc, .pyo, .pyd
            if file.endswith(".py") and not file.endswith(('.pyc', '.pyo', '.pyd')):
                file_path = os.path.join(root, file)
                
                # Check if file is readable text (not binary/compiled)
                try:
                    with open(file_path, 'rb') as f:
                        chunk = f.read(512)
                        # Check if file contains non-text bytes (compiled/encoded)
                        if b'\x00' in chunk:
                            print(f"⚠️ Skipping binary/compiled file: {file_path}")
                            continue
                except Exception as e:
                    print(f"⚠️ Error checking file {file_path}: {e}")
                    continue
                
                convert_py_to_pdf(file_path, output_dir)


if __name__ == "__main__":
    # Default path to python_files folder
    default_path = r"E:\All\mentee_tracker_mca\python_files"
    
    # Check if path is provided as command-line argument
    if len(sys.argv) > 1:
        input_base_dir = sys.argv[1]
    else:
        user_input = input(f"Enter the base folder path containing .py files (press Enter to use default: {default_path}): ").strip()
        input_base_dir = user_input if user_input else default_path

    if not os.path.exists(input_base_dir):
        print(f"❌ The provided path does not exist: {input_base_dir}")
    else:
        print("🚀 Starting conversion...\n")
        convert_all_py_recursively(input_base_dir)
        print("\n🎉 Conversion completed! All PDFs saved inside 'pdf_outputs/' folder.")


