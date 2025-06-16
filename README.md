# Sharenv
A basic way to write variables in Bash and share them to Fish... irresponsibly.

### Word of Warning
Sharenv is able to setup variables between different shells because it generates
the right kind of shell script for the right shell, however, there is no better
way to parse this other than a live call to `eval`. This is generally not a good
idea nor a good design principal as it can open the user to attack vectors
regardless of the checks I have placed to restrict such a thing from happening.
Keep this in mind if you are to use this **personal** software of mine.

### Install
```sh
pip install git+https://github.com/cyrus01337/sharenv.git#egg=sharenv
```

### Usage
```sh
# ~/.bashrc
# ~/.config/fish/config.fish

# auto-detects current running shell
eval "$(sharenv)"

# you can also manually specify it
eval "$(sharenv --shell fish)"
```
