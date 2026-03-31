.. _app-templates:

App Templates
=============

Find the source code for the templates on `GitLab <https://gitlab.com/clickable/ut-app-meta-template>`__.

QML Only
--------

An app template that is setup for a purely QML app. It includes a CMake setup
to allow for easy translations.

C++
---

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

Rust
----

An app template that is setup for a QML app with a Rust backend.

Godot (Precompiled)
-------------------

An app template that is setup to package a precompiled Godot app together with
a patched Godot and SDL 2 build.

SDL
---

An app template that is setup for an SDL app. It includes both SDL3 and SDL2
through `sdl2-compat <https://github.com/libsdl-org/sdl2-compat>`__, as well as
satellite libraries like SDL_image, SDL_ttf, SDL_mixer and SDL_net, both
versions 2 and 3.

The template provides information to assist developers wishing to port existing
apps based on SDL to Ubuntu Touch; another good information source is the
`SDL docs for Ubuntu Touch <https://github.com/libsdl-org/SDL/blob/main/docs/README-ubuntu-touch.md>`__.
