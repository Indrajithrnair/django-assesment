#!/usr/bin/env python
"""Test script to verify WSGI configuration"""

import importlib

try:
    # Try to import the WSGI application object
    wsgi_module = importlib.import_module('assessment.wsgi')
    application = getattr(wsgi_module, 'application')
    print("✅ Successfully imported WSGI application!")
    print(f"Module: {wsgi_module.__name__}")
    print(f"Application object: {application}")
except Exception as e:
    print(f"❌ Error importing WSGI application: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nWSGI configuration looks correct.")
print("You can run your application with: gunicorn assessment.wsgi:application") 