Common Experience
=================

Following success of [CK (Collective Knowledge) framework](https://github.com/ctuning/ck)
and based on the experience of using it (hence the name),
here we attempt to re-design certain assumptions central to the CK framework's kernel
which cannot be simply evolved from its current state
due to the requirement of code's backwards compatibility.


The goal here is to retain compatibility with the core ideas and the spirit of CK.


Main concepts of the CE system:
===============================

1) An entry is a directory that can contain:
    - JSON meta-file with parameters (including tags and attributes) - in "own_parameters.json"
    - runnable code - in "own_methods.py"
    - other contained data files
with a simple universal interface.

2) An entry can inherit certain aspects from another entry -
code, parameters and, to some extent, included data files.
Each entry can keep its own list of parents in its own_parameters.
There are no "classes" in this OO model - only "instances" inheriting (with override)
from other "instances".
If an entry does not declare its parents, it inherits from the "base_entry"

3) Inherited aspects of an entry are overridable:
    - JSON meta-file is edited on-the-fly using patching methods (simple merger or json-patch)
    - runnable code can be overridden by same-name methods in the derived entry
    - data files can be inherited if properly pre-declared and referenced from meta-file

4) Collections. Spatial organization of the knowledge base:
if an entry (being a directory) contains other entries, it may be treated as a "collection"
that knows about its constituents and can find them easily using a variety of storable indices
(primarily using tags and attributes).
    A collection *contains* an index by which its constituent entries can be found
    (either relative to its own path or absolute):

Three notable collections:
    1) "core_collection" is installed as part of CE and contains "internal" entries of the system (such as "clip_parser", etc)
    2) "working_collectin" is created in user's home directory to keep all the objects the user will be working with.
        It supersedes CK, CK_TOOLS and CK/local directories, but being an entry itself can be operated by standard CE tools.

    ce bypath ~/alt_collection \
        findN env,model_type=onnx \
        tabulate eid,name,version,tags

working_collection/own_parameters.json:

    {
        "parent_entry_name": "core_collection",
        "name2path": {
            "foo_entry": "",
            "deeper_entry": "under/serveral/internal/directories",
            "nested_collection_A": "",
            "core_collection": "/absolute/path/to/ce"
        },
        "chained_collections": ["nested_collection_A", "core_collection"]
    }

All searches are assumed to start from working_collection:

    ce from1 deeper_entry \                                     # search the index by name (and recursively in chained_collections if not found)
        foo_action --bar=10 --baz=25

    ce find1 env,model_type=tflite,channel_order=nchw,resnet \  # search the collection by query (and recursively in chained_collections if not found)
        cat


------------------------------------------------------------------------------------------------

4) Generalized dependencies:
    "deps" is an *array* (not dictionary) of independent conditions by which entries have to be found.
    For each condition either a single entry is found, or a method is called to rectify the situation.
    This method either returns an entry (by either setting it up or selecting it), or some kind of
    "unable to set up" signal, whereby the whole "resolve" call is considered to have failed.

    ce run program_xyz --deps[name=weights].tags+=tflite

   Forming/adding deps on the fly:
    ce virtual env --deps=+{tags:x,!y;z} --deps=+{tags:p,q,!r}

    ce from env \
        tweak --deps=+{tags:x,!y;z} --deps=+{tags:p,q,!r} \
        shell

   Another example is the dependency of some entries on other collections.
   Specific details on how to resolve entry-on-collections dependency are different,
   yet the underlying mechanism is the same.

------------------------------------------------------------------------------------------------
