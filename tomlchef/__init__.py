"""
TOMLChef
========

With TOMLChef, you can
  1. Break down complex applications into isolated, manageable components
     called Jobs.
  2. Generate configuration files (so-called Recipes) from which Jobs can be
     built and run. They are stored in the humanly readable TOML format.
  3. Benefit from automatic validation of configuration values, such as
     checking for path validity, working directory corruption, and more.
  4. Access a commandline interface to generate Recipes and execute Jobs.
  5. Make use of a robust logging backend.
  6. Configure a global seed to be used by all packages.

Writing applications with TOMLChef is simple. Inside your application package,
create an entry script (e.g., ``main.py``) and add the following:

.. code-block:: python

    from tomlchef import Application

    app = Application(Path(__file__).parent)
    app.run()

To register a new Job to the TOMLChef framework, inherit from ``tomlchef.Job``
and register your class, like so:

.. code-block:: python

    from tomlchef import Job

    @tomlchef.registered_job
    class MyCustomJob(Job):

        def __init__(self, foo: int, bar: str, **kwargs):
            super.__init__(self, **kwargs)
            self.foo = foo
            \"\"\"
            Docstring for foo.
            \"\"\"

            self.bar = bar
            \"\"\"
            Some docstring for bar.
            \"\"\"

        def _is_finished():
            return True # Is the job done?

        def _run():
            pass # Code here executes if _is_finished returns False

        def _setup():
            pass # Code here always executes, before _run

        def _exit():
            pass # Code here always executes, after _run


You can now generate a recipe for this job, by opening a terminal and running:

.. code-block:: sh

    python my_package/main.py recipe MyCustomJob -o my_custom_job_recipe.toml

The generated recipe looks like this:

.. code-block:: toml

    type = "MyCustomJob"

    [stats]
    app_version = "0.0.1"
    created_on = "2024-06-14T19:36:39+00:00"

    [misc]
    log_level = "INFO" # DEBUG, INFO, WARN, ERROR, CRITICAL, OFF

    [misc.tqdm]
    disable_progress_bars = false
    erase_completed_progress_bars = false

    [job]
    root = "" # Working directory; the job will be created here

    rng_seed = 0 # Set a global seed for all libraries

    [my_custom_job]
    foo = 0 # Docstring for foo.
    bar = "" # Some docstring for bar.

Docstrings for member variables are automatically included as well, which makes
it easy to document Recipes without needing to duplicate documentation.
"""

from ._version import __version__
