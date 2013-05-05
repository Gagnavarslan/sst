import os
from sst import loader as sloader


def discover(loader, directory, name):
    return loader.discoverTestsFromPackage(
        __package__,
        os.path.join(directory, name),
        file_loader_class=sloader.ModuleLoader,
        dir_loader_class=sloader.PackageLoader)
