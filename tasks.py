import glob
import os
import shutil
import tarfile

from invoke import task


@task
def build(c):
    shutil.rmtree("dist", ignore_errors=True)
    c.run("python -m build --sdist --wheel .")


@task
def html(c):
    c.run("sphinx-build -b html doc/source doc/build")


@task
def tag(c):
    import pyrequire
    
    c.run(f"git tag v{pyrequire.__version__}")
    c.run("git push --tags")


@task
def clean(c, bytecode=False):
    patterns = [
        "build",
        "dist",
        "pyrequire.egg-info",
        "doc/build",
        "doc/source/examples",
    ]

    if bytecode:
        patterns += glob.glob("**/*.pyc", recursive=True)
        patterns += glob.glob("**/__pycache__", recursive=True)

    for pattern in patterns:
        if os.path.isfile(pattern):
            os.remove(pattern)
        else:
            shutil.rmtree(pattern, ignore_errors=True)


@task
def ruff(c):
    c.run("ruff check --fix pyrequire tests")
    c.run("ruff format --target-version py38 --line-length 88 pyrequire tests")


@task
def tar(c):
    patterns = [
        "__pycache__",
    ]

    def filter(filename):
        for pattern in patterns:
            if filename.name.endswith(pattern):
                return None

        return filename

    with tarfile.open("pyrequire.tar.gz", "w:gz") as tf:
        tf.add("pyrequire", arcname="pyrequire/pyrequire", filter=filter)
        tf.add("pyproject.toml", arcname="pyrequire/pyproject.toml")


@task
def test(c, cov=False, html=False):
    command = ["python -m pytest"]

    if cov:
        command += ["--cov", "pyrequire", "--cov-report", "term"]

        if html:
            command += ["--cov-report", "html"]

    command += ["tests"]

    c.run(" ".join(command))
