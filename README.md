# [Clickable](https://clickable-ut.dev/en/latest/)

Compile, build, deploy an debug Ubuntu Touch click packages all from the command line.

## Docs

* [Install](https://clickable-ut.dev/en/latest/install.html)
* [Getting Started](https://clickable-ut.dev/en/latest/getting-started.html)
* [Usage](https://clickable-ut.dev/en/latest/usage.html)
* [Commands](https://clickable-ut.dev/en/latest/commands.html)
* [Project Config Format](https://clickable-ut.dev/en/latest/clickable-json.html)
* [App Templates](https://clickable-ut.dev/en/latest/app-templates.html)
* [Builders](https://clickable-ut.dev/en/latest/builders.html)

## Code Editor Integrations

Start QtCreator shipped by Clickable in a project folder via `clickable ide`.

## Development

Please base any development on the branch `dev` and file merge requests against it.

### Run Clickable from Repository

You can run Clickable directly from sources via the `clickable-dev` script.
Add the `--verbose` option for additional output.

It is recommended to add your clickable repo folder to `PATH`.
This can be done by adding `export PATH="$PATH:$HOME/clickable"` to your `.bashrc`.
Replace `$HOME/clickable` with your path.

To enable configuration validation either install **jsonschema** via pip
(`pip3 install jsonschema`) or apt (`apt install python3-jsonschema`). If you
got Clickable regularly installed, you already have jsonschema, too.

### Linting

Clickable uses flake8 and pylint for linting as well as autopep8 for formatting.
Install them using `pip3 install flake8 pylint autopep8`.
Run `make lint` to lint and `make format` to format the source code.

### Run the tests

Install the pytest modules: `pip3 install pytest pytest-cov`.

Run pytest to complete the tests: `make test`.

### Related Repositories

* [Clickable docker images and app templates](https://gitlab.com/clickable)

## License

Copyright (C) 2022 Clickable Team

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3, as published
by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
