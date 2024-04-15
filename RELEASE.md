# Releases

This document is a reminder for maintainers on how to perform a release.

Feature changes and Bug Fixes are merged into `dev` and find there way to the `master`
branch only during a Release. In contrast, documentation fixes may be merged directly
into `master` to make them available more quickly.

The following sections describe how to perform a release. Note that most of it can
be automated with `scripts/update-version.py`.

## Update Merge Request

Check out the `dev` branch.

Create a commit with the following changes:

* Add the change log as bullet points to `debian/changelog` and `docs/changelog.rst`.
* In `clickable/version.py`, change `__version__` and  
`__container_minimum_required__`, if applicable.
* Change `docs/_static/version.json`
* Change `version` and `release` in `docs/conf.py`

Note: Include changes to the Clickable Docker Images and App Templates to the changelog,
even though they are released (partially) independently.

As commit message write `Bump version to x.x.x` (inserting the new version number).

Push the commit to `dev` on Gitlab and create a Merge Request from `dev` to `master`.
Make sure to **unset(!)** the `Squash commits` check box.

## Publishing

After reviewing and merging the Update Merge Request, trigger the CI publish
jobs by creating a light-weight tag on `master` in the format `vx.x.x` (e.g. `v8.0.1`).
Wait until the CI pipeline finished. Then create the same tag on the `master` branch
in the `clickable/clickable-docker-images` repository. This will trigger the release
of images tagged with the release version as well as CI images shipping the new version
of Clickable.

Log into [Snapcraft](https://snapcraft.io/clickable/releases) and pull the new version
into the **latest/stable** channel. Changes on the master branch get released on
the **edge** channel automatically.

Changes to the Documentation get published via a Webhook on any push event on
the master branch.

## Direct Changes on Master

In case, changes were pushed directly into `master` or merged from a branch
other than `dev` (e.g. for documentation quick fixes), create a Merge Request
from `master` to `dev`. Make sure to **unset(!)** the `Squash commits` check box.

## Version Numbers

Clickable follows the [Semantic Versioning](https://semver.org/) model.

Clickable Docker Images are labeled with an `IMAGE_VERSION` containing a single number.
This version is independent from the Clickable version. It is incremented on
changes that a feature in Clickable relies on. It allows Clickable to check whether
the user has downloaded a recent-enough Clickable docker image for the features it
shifts.
