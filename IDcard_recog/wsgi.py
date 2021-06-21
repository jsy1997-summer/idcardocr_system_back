"""
WSGI config for IDcard_recog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IDcard_recog.settings")
#这里要增加这一行代码，类似于环境变量的path
sys.path.append('E:/IDcard_recog/IDcard_recog/IDcard_recog')

application = get_wsgi_application()
