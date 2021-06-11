#!/usr/bin/env python3

import requests
import sys

sys.path.insert(0, '../clickable')
from clickable.commands.create import TEMPLATE_MAP  # noqa=E402

response = requests.get(
    'https://gitlab.com/clickable/ut-app-meta-template/-/raw/master/cookiecutter.json',
    timeout=5
)
response.raise_for_status()
template_json = response.json()

templates = template_json['Template']
create_templates = list(TEMPLATE_MAP.values())

superfluous = list(set(create_templates) - set(templates))
missing = list(set(templates) - set(create_templates))

for s in superfluous:
    print("Template '{}' in create command does not exist in template repo.".format(s))

for m in missing:
    print("Template '{}' from template repo is missing in create command.".format(m))

if superfluous or missing:
    sys.exit(1)
