{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python39
    pkgs.python39Packages.django.override { withGdal = true; }
    pkgs.python39Packages.psycopg2
    pkgs.python39Packages.django-environ
    pkgs.python39Packages.djangorestframework
    pkgs.python39Packages.beautifulsoup4
    pkgs.python39Packages.celery
    pkgs.python39Packages.sqlparse
    pkgs.python39Packages.tzdata
    pkgs.python39Packages.gunicorn
    pkgs.python39Packages.aiohttp
    pkgs.python39Packages.dj-database-url
    pkgs.python39Packages.uvicorn
    pkgs.python39Packages.django-cors-headers
    pkgs.python39Packages.psutil
    pkgs.python39Packages.django-redis
    pkgs.gdal
  ];

  shellHook = ''
    export GDAL_LIBRARY_PATH=${pkgs.gdal}/lib/libgdal.so
  '';
}