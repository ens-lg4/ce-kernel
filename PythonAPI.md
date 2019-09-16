
CE Python API
=============

As simple as possible

Summary of methods
------------------

    object = ce.from_dict()         - build a CE in-memory object from the given dictionary

    object = ce.from_path()         - load a CE memory object from a given fs path

    object["field"]                 - hard access to a field (assumes it exists or sets it)

    object.get("field")             - soft access to a field (returns None if did not exist)

    object.verb( { call-params })   - calling an object's method

    object.pipe( chain-of-calls )   - calling a chain of calls on the current object

# ------------------------------

import ce

working_collection_path = os.path.join( getenv('HOME'), 'working_collection' )

# loading a stored object from path
working_collection = ce.from_path( working_collection_path )

# calling methods on objects
alice_entry = working_collection.find1({
    "query": "name=Alice,country=Argentina,female"
})

# accessing fields of an object (raises exception if missing)
a_country = alice_entry["country"]

# soft-accessing fields of an object (returns None if missing)
a_phone = alice_entry.get("phone")

# creating an unstored entry from a dictionary
bob_entry = ce.from_dict( {"name": "Bob", "country": "Bangladesh", "family": "Keymaker"} )

# storing a dynamically-created object
bob_entry.save({
    "entry_name": "bob_entry",
    "collection": working_collection_path
})

# calling a pipeline that starts from an object
# Q1: should a copy be made from it first?
# Q2: tweak input format?
# Q3: reusing pipe's input format for storing pipes?
working_collection.pipe( [
    ["from", "python-package-tensorflow-1.12"],
    ["tweak", { "action": "set", "key_path": ".version", "value": "1.13"} ],
    ["save", { "entry_name": "python-package-tensorflow-1.13"} ]
] )
