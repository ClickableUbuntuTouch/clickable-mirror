.. _app-templates:

App Templates
=============

Find the source code for the templates on `GitLab <https://gitlab.com/clickable/ut-app-meta-template>`__.

QML Only
--------

An app template that is setup for a purely QML app. It includes a CMake setup
to allow for easy translations.

C++ (Plugin)
------------

An app template that is setup for a QML app with a C++ plugin. It includes a CMake
setup for compiling and to allow for easy translation.

Python
------

An app template that is setup for an app using Python with QML. It includes a
CMake setup to allow for easy translation.

HTML
----

An app template that is setup for a local HTML app.

Go
--

An app template that is setup for a QML app with a Go backend.

C++ (Binary)
------------

An app template that is setup for a QML app with a main.cpp to build a custom
binary rather than relying on qmlscene. It includes a CMake setup for compiling
to allow for easy translation.

Rust
----

An app template that is setup for a QML app with a Rust backend.

SDL
---

An app template that is setup for an SDL app. It includes both SDL3 and SDL2
through `sdl2-compat <https://github.com/libsdl-org/sdl2-compat>`__, as well as
satellite libraries like SDL_image, SDL_ttf, SDL_mixer and SDL_net, both
versions 2 and 3.

The template provides information to assist developers wishing to port existing
apps based on SDL to Ubuntu Touch; another good information source is the
`SDL docs for Ubuntu Touch <https://github.com/libsdl-org/SDL/blob/main/docs/README-ubuntu-touch.md>`__.
