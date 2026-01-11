#!/usr/bin/env python3
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
django_project_path = os.path.join(project_root, 'django-lms')

print(f"Script dir: {script_dir}")
print(f"Project root: {project_root}")
print(f"Django project path: {django_project_path}")
print(f"Exists: {os.path.exists(django_project_path)}")

if os.path.exists(django_project_path):
    sys.path.insert(0, django_project_path)
    print(f"Added to path: {django_project_path}")
else:
    print("ERROR: Django project path not found!")
    sys.exit(1)
