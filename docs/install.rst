.. _install:

Install
=======

Install Via Pip (Recommended)
-----------------------------

* Install docker, adb, git and python3 and pip3 (Ubuntu 18.04) or pipx (Ubuntu 20.04 or higher)

  * pip3: ``sudo apt install docker.io adb git python3 python3-pip python3-setuptools``
  * pipx: ``sudo apt install docker.io adb git python3 pipx python3-setuptools``

* Run

  * pip3: ``pip3 install --user clickable-ut``
  * pipx: ``pipx install clickable-ut``

* Add pip scripts to your PATH: ``echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc`` and open a new terminal for the setting to take effect

* Alternatively, to install nightly builds

  * pip3: ``pip3 install --user git+https://gitlab.com/clickable/clickable.git@dev``
  * pipx: ``pipx install git+https://gitlab.com/clickable/clickable.git@dev``

To update Clickable
  * pip3: ``pip3 install --user clickable-ut --upgrade``
  * pipx: ``pipx upgrade clickable-ut``

Install Via Python Virtual Environment (Alternative)
----------------------------------------------------

* Install docker, adb, git, python3 and pip3
  (in Ubuntu: ``sudo apt install docker.io adb git python3 python3-pip python3-setuptools python3-venv``)
* Run:

.. code-block:: bash
   :linenos:

   # Create a virtual environment called .venv
   python3 -m venv .venv --system-site-packages
   # Activate the virtual env
   source ./.venv/bin/activate
   # Install clickable
   pip install clickable-ut --upgrade
   # Create clickable app
   clickable create --dir ./


Install as Snap
---------------
* Make sure you have `snapd installed <https://snapcraft.io/docs/installing-snapd>`__.
* Run:

.. code-block:: bash
   :linenos:

   # Install clickable and docker
   sudo snap install clickable
   sudo snap install docker
   # Add connections
   sudo snap connect clickable:raw-usb
   sudo snap connect clickable:docker docker
   sudo snap connect clickable:home
   sudo snap connect clickable:removable-media
   sudo snap connect clickable:network
   sudo snap connect clickable:network-bind
   sudo snap connect clickable:ssh-keys
   sudo snap connect clickable:ssh-public-keys
   sudo snap connect clickable:adb-support

Install Via PPA (Ubuntu)
------------------------

* Add the `PPA <https://launchpad.net/~bhdouglass/+archive/ubuntu/clickable>`__ to your system: ``sudo add-apt-repository ppa:bhdouglass/clickable``
* Update your package list: ``sudo apt-get update``
* Install clickable: ``sudo apt-get install clickable``

Install Via AUR (Arch Linux)
----------------------------

* Using your favorite AUR helper, install the `clickable-git package <https://aur.archlinux.org/packages/clickable-git/>`__
* Example: ``pacaur -S clickable-git``

After install
-------------

* Let Clickable setup docker (asking for root permissions) and bash completion: ``clickable setup``
* Log out or restart to apply changes if requested
