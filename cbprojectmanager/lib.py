"""Module for creating and updating the project / database

Note :
    Some function are derived from avalon.io, some are not available in
    avalon.io.

"""
import json
import os
import sys
import time
from copy import deepcopy
import logging

import pymongo
import bson

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
    collections = list(self._database.collection_names())
    if name in collections:
        raise RuntimeError("Collection with name `%s` already exists" % name)

    collection = self._database.create_collection(name)
    assert get_collection(name), "This is a bug!"

    return collection


def drop_collection(nam_or_collection):
    self._database.drop_collection(nam_or_collection)


def create_project_definition(collection, data):
    """Create a project definition in the given colleciton

    When giving a divert keys, the function will temporarely take this
    information from the data to ensure `schema.validate` is successful.

    Args:
        collection(pymongo.collection.Collection): collection from database
        data(dict): project data

    Returns:
        bson.ObjectId

    """

    # Validate data for project
    data["schema"] = "avalon-core:project-2.0"
    schema.validate(data)

    # Check if the name is unique
    exists = collection.find_one({"type": "project", "name": data["name"]})
    if exists:
        raise RuntimeError("Project with name `%s` already exists in this "
                           "collection `%s`" % (data["name"], collection.name))

    result = collection.insert_one(data)
    assert result.acknowledged, ("Could not create project definition, "
                                 "please contact a Pipeline TD!")

    return result.inserted_id


def create_project(name, template=None):
    """Create a new collection and project

    Args:
        name(str): name of the new project
        template(dict): preset data definition to use

    Returns:
        bool

    """

    if template:
        data = deepcopy(template)
        data.update({"name": name})
    else:
        data = {"name": name,
                "type": "project",
                "data": {},
                "config": {
                    "template": {},
                    "tasks": [],
                    "apps": []
                }}

    collection = create_collection(name)
    try:
        create_project_definition(collection, data)
    except Exception as exception:
        print("Ran into a little problem!")
        print(exception)
        print(".. Dropped collection")
        drop_collection(name)

        return False

    return True


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
    """Get the project document by name

    Args:
        name(str): name of the project
    Returns:
        dict

    """
    projects = [p for p in list(get_projects()) if p["name"] == name]
    if len(projects) == 1:
        return projects[0]

    return


def get_project_template(name_or_project):
    """Return the template of a project

    The function will strip out the project's name and unique ID to make it
    a reusable template

    Args:
        name_or_project(name, dict): name or project document

    Returns:
        dict

    """
    if isinstance(name_or_project, str):
        document = get_project(name_or_project)
    elif isinstance(name_or_project, dict):
        document = name_or_project
    else:
        raise TypeError("Input type `%s` not supported" % type(name_or_project))

    # Omit key, value pairs which make the project unique
    for key in ["name", "_id"]:
        document.pop(key, None)

    return document


def get_template():
    """Get the project template from"""

    module_dir = os.path.dirname(__file__)
    template_path = os.path.join(module_dir, "res", "base_template.json")

    with open(template_path, "r") as f:
        template = json.load(f)

    return template
