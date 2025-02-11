import os
import shutil
from datetime import datetime

# Define paths
date_str = datetime.now().strftime('%Y-%m-%d')
date_directory = f'/tmp/html-report/{date_str}'
index_file_path = '/tmp/html-report/index.html'
dest_path = '/shared/html-report'

# Get list of HTML files
html_files = [f for f in os.listdir(date_directory) if f.endswith('.html')]

# Create index.html content
index_content = "<html><body>\n"
index_content += f"<h1>PRCC prod Servers HTML Report for {date_str}</h1>\n<ul>\n"

for html_file in html_files:
    index_content += f'<li><a href="{date_str}/{html_file}">{html_file}</a></li>\n'

index_content += "</ul>\n</body></html>"

# Write index.html
with open(index_file_path, 'w') as index_file:
    index_file.write(index_content)

# Copy the directory and files from /tmp/html-report/ to /shared/html-report/
shutil.copytree('/tmp/html-report', '/shared/html-report', dirs_exist_ok=True)

print(f'Index file created at: {index_file_path}')
print(f'Files copied from {date_directory} to {dest_path}')
