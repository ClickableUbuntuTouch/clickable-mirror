#!/usr/bin/env python3

import sys
import re
import ast
import json
from datetime import datetime

if len(sys.argv) != 2:
    raise Exception('Must supply a version number')

version = sys.argv[1]
if not re.match(r'^\d+\.\d+\.\d+$', version):
    raise Exception('Invalid version passed')

version_re = re.compile(r'__version__\s+=\s+(.*)')
version_file = 'clickable/version.py'
with open(version_file, 'rb') as f:
    current_version = str(ast.literal_eval(version_re.search(
        f.read().decode('utf-8')).group(1)))

if version <= current_version:
    raise Exception('Version must be greater than the current version')

print(f'current version: {current_version}, new version: {version}')

version_json_file = 'docs/_static/version.json'
with open(version_json_file, 'r') as fr:
    version_json = json.load(fr)
    version_json['version'] = version

    with open(version_json_file, 'w') as fw:
        json.dump(version_json, fw, indent=4)

print(f'updated {version_json_file}')

docs_conf_file = 'docs/conf.py'
with open(docs_conf_file, 'r') as fr:
    docs_conf = fr.readlines()
    updated_docs_conf = []
    for line in docs_conf:
        if line.startswith('version ='):
            updated_docs_conf.append(f'version = \'{version}\'\n')
        elif line.startswith('release ='):
            updated_docs_conf.append(f'release = \'{version}\'\n')
        else:
            updated_docs_conf.append(line)

    with open(docs_conf_file, 'w') as fw:
        fw.write(''.join(updated_docs_conf))

print(f'updated {docs_conf_file}')

with open(version_file, 'r') as fr:
    version_data = fr.readlines()
    updated_version_data = []
    for line in version_data:
        if version_re.match(line):
            updated_version_data.append(f'__version__ = \'{version}\'\n')
        else:
            updated_version_data.append(line)

    with open(version_file, 'w') as fw:
        fw.write(''.join(updated_version_data))

print(f'updated {version_file}')

deb_changelog_file = 'debian/changelog'
with open(deb_changelog_file, 'r') as fr:
    deb_changelog = fr.readlines()
    date_string = datetime.now().strftime('%a, %d %b %Y %H:%M:%S')
    deb_changelog = [f'clickable ({version}) unstable; urgency=medium\n\n\
  * TODO\n\n\
 -- Clickable <bhdouglass+clickable@gmail.com>  {date_string} -0500\n\n'] + deb_changelog

    with open(deb_changelog_file, 'w') as fw:
        fw.write(''.join(deb_changelog))

print(f'added entry to {deb_changelog_file}')

docs_changelog_file = 'docs/changelog.rst'
with open(docs_changelog_file, 'r') as fr:
    docs_changelog = fr.readlines()
    docs_changelog.insert(5, f'Changes in v{version}\n-----------------\n\n- TODO\n\n')

    with open(docs_changelog_file, 'w') as fw:
        fw.write(''.join(docs_changelog))

print(f'added entry to {docs_changelog_file}')
