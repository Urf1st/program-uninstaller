import pathlib
import shutil

def leftover_searcher(package_name, source):
    search_dir = [
        pathlib.Path.home() / ".config",
        pathlib.Path.home() / ".local",
        pathlib.Path.home() / ".cache",
        pathlib.Path.home() / ".var"
    ]
    found = []
    for search in search_dir:
        for path in search.rglob("*"):
            if package_name.lower() in path.name.lower():
                found.append(str(path))
    return (found)

def remove_leftover(path_str):
    try:
        p = pathlib.Path(path_str)
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
        return True
    except Exception:
        return False