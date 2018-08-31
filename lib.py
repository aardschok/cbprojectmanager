"""Module for creating and updating the project / database

Note :
    Some function are derived from avalon.io, some are not available in
    avalon.io.

"""

import logging
import sys
import time

import pymongo

from avalon import api, schema

__DATABASE_NAME = "avalon"
self = sys.modules[__name__]
self._mongo_client = None
self._database = None
self._is_installed = False

log = logging.getLogger(__name__)


def install():
    """Establish a connection with the database"""

    if self._is_installed:
        return

    mongo_url = api.Session["AVALON_MONGO"]

    timeout = 1000
    self._mongo_client = pymongo.MongoClient(mongo_url,
                                             serverSelectionTimeoutMS=timeout)

    for retry in range(3):
        try:
            t1 = time.time()
            self._mongo_client.server_info()

        except Exception:
            log.error("Retrying..")
            time.sleep(1)
            timeout *= 1.5

        else:
            break

    else:
        raise IOError(
            "ERROR: Couldn't connect to %s in "
            "less than %.3f ms" % (mongo_url, timeout))

    log.info("Connected to %s, delay %.3f s" % (mongo_url, time.time() - t1))

    database_name = api.Session.get("AVALON_DB", __DATABASE_NAME)
    self._database = self._mongo_client[database_name]


def create_collection(name):
    """Create a new collection in the current database

    Args:
        name(str): name of the new collection

    """

    # Check if name is not already taken
    collections = self._database.list_collection_names()
    if name in collections:
        raise RuntimeError("Collection with name `%s` already exists" % name)

    collection = self._database.create_collection(name)
    assert name in self._database, "This is a bug!"

    return collection


def create_project_definition(collection, data):

    # Validate data for project
    data["schema"] = "avalon-core:project-2.0"
    schema.validate(data)
    data.pop()

    # Check if data is not already present
    exists = collection.find_one({"type": "project", "name": data["name"]})
    if exists:
        raise RuntimeError("Project with name `%s` already exists in this "
                           "collection `%s`" % (data["name"], collection.name))

    collection.insert_one(data)

    pass


def get_database_name():
    return self._database.name


def get_collection(name):

    exists = next(c for c in self._database.collection_names()
                  if c == name)
    if not exists:
        raise RuntimeError("Could not find collection with name `%s`" % name)

    collection = self._database.get_collection(name)

    return collection


def get_projects():
    """List available projects

    Returns:
        list of project documents

    """

    for project in self._database.collection_names():
        if project in ("system.indexes",):
            continue

        # Each collection will have exactly one project document
        document = self._database[project].find_one({
            "type": "project"
        })

        if document is not None:
            yield document


def get_project(name):
    """Get the project by name

    Args:
        name(str): name of the project
    """

    projects = list(get_projects())
    project = next(p for p in projects if p["name"] == name)

    return project