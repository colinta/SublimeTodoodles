 Todoodles for Sublime Text 3
==============================

A Todo-list language syntax, key bindings, and plugins to make managing a
text-based TODO list easy.

Other Todo plugins like this go too far, I think, and try to completely control
your editor.

 Usage
-------

Use the "Todoodles" language syntax (file extension "todolist").  I used generic
scope names in the language syntax, so you don't need to use a custom theme or
anything like that.

To create a TODO, start any line with `[ ] `, followed by the TODO title.

    [ ] Finish this README

For ease-of-use, the `+` and `=` buttons will also start a new TODO, but again
only if you're at the beginning of the line (or indented).

From anywhere in the line, you can press `shift+space, space` to mark the task
complete.  or `shift+space, !` for urgent, `shift+space, .` for generic mark
(current?, low-priority?, whatever you want), and `shift+space, ?` for unknown
status.  If you're at the front of the line, in the brackets, you can use just
the ` !.?` character.

    [✓] Finish this README


 Installation
--------------

1. Using Package Control, install "Todoodles"

Or:

1. Open the Sublime Text 3 Packages folder

    - OS X: ~/Library/Application Support/Sublime Text 3/Packages/
    - Windows: %APPDATA%/Sublime Text 3/Packages/
    - Linux: ~/.Sublime Text 3/Packages/

2. clone this repo
3. Install keymaps for the commands (see Example.sublime-keymap for my preferred keys)
