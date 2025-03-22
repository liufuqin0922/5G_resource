import os; os.system('cat > fix_views.py << "EOF"
with open("core/views.py", "r") as f:
    content = f.read()

content = content.replace("filename=\"resources.xlsx\"", "filename=\'resources.xlsx\'")

with open("core/views.py", "w") as f:
    f.write(content)
EOF')
