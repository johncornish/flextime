# Description

A hierarchical task management tool that also attempts to optimally
schedule task nodes to configured blocks of time throughout the
week. See the examples directory for an explanation of how to
structure your `tasks.yml` and `schedule.yml`.

# Installation

`pip install flextime`

This will install the package and provide the executable `ft` (if
you've properly configured your Python environment).

# Usage

The purpose of each CLI command, as well as its arguments and options,
is briefly explained via the `--help` flag, or by running `ft` without
any arguments, but I will also give a synopsis here. Commands run
without file arguments assume files exist in the current directory;
reference the help for how to pass custom file paths.

All of the following commands present the user with an interactive
menu. `show` and `list` accept digits as indexes (within the current
page) of tasks to complete (remove) and `add` facilitates traversal
through the task tree.

`ft show`

Attempt to optimally schedule `tasks.yml` task nodes to time blocks
configured in `schedule.yml`.

`ft list`

Present task nodes in a list, optionally sorting by the provided
attribute short names. For example, `ft list d t` would sort first by
date and then by time estimate.

`ft add`

Display the top level of each subtree, allowing the user to traverse
the tree and add nodes or additional subtrees.