# pylint: disable=missing-module-docstring
class Job:
    """
    A ``Job`` is an abstraction for any principal component of your
    application, such as data processing or model training.

    The working directory of a Job ``j`` is ``j.root``, where the Job data are
    stored.
    Except for other Jobs and input data, a Job
    should be fully self-contained at its ``root`` to avoid file scatter
    and enable easy relocation to another disk or machine.

    The storage format for serialized Jobs is TOML. All Jobs have basic
    metadata, such as type, creation date and application
    version. Subclasses of ``Job`` can maintain additional, Job-specific
    metadata.

    Subclasses must implement the methods specified in
    ``BaseMeta.methods_to_implement``. Refer to the documentation of each
    method for details.

    Notes
    -----
    Any field with prefix "_external" in ``Job`` and its subclasses is assumed
    to be an external path (or list of paths) pointing to a location outside
    ``root``. Such paths are automatically validated when executing a job,
    and a ``FileNotFoundError`` is raised if an external path has become
    invalid.
    """
    pass
