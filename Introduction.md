CE (Common Experience) is a hacker's tool for running everyday experiments,
with a special stress on reproducibility.

Similar to UNIX operating system, it is designed to consist of:
* a relatively small kernel that does internal magic,
* a user-extensible knowledge base made of "entries" and
* a powerful command line interface that allows to combine the "entries" in a myriad of useful ways.

Entries
=======

Each entry is a directory that may contain code, data or both,
to which a straightforward standardised interface is provided.

Code-containing entry
---------------------

Every directory on the filesystem can be instantly converted into an entry by adding an extra file to it.

We shall create the simplest entry that contains python code:
```
	mkdir alice_entry

	cat <<EOF >alice_entry/own_methods.py
	def say_hello(name):
		print("Hello, "+name+"!")
	EOF
```

Let's run it. In the command line below we use "method/action chaining", which means we first have to reach the entry,
and then run an action from it:
```
	ce bypath alice_entry \
	   say_hello
ERROR: Not enough parameters for running say_hello()
```

Uh-oh... Indeed, **say_hello** requires a *name*, so let's supply it this time:
```
	ce bypath alice_entry \
	   say_hello Bob
Hello, Bob!
```

You may have noticed that we split the command line into two parts, even though it is not very long.
This is purely for readability. Each part starts with an action/verb which is followed by its parameters:
* **bypath** is a core action for loading an entry from a given path
* **say_hello** is the action from this entry that we have just defined

Data-containing entry
---------------------

Let's now add data to the same entry:
```
	echo '{ "name": "Alice", "family": "Keymaker", "country": "Argentina" }' > alice_entry/own_parameters.json
```

Again, we can access this data straight away using the existing infrastructure:
```
	ce bypath alice_entry \
	   tabulate name
Alice

	ce bypath alice_entry \
	   tabulate name,family,country --separator ' : '
Alice : Keymaker : Argentina
```

The new core action **tabulate** displays a subset of the data in a formatted way.


Now let's try to run the **say_hello** action from above, but omit its *name* parameter:
```

	ce bypath alice_entry \
	   say_hello
Hello, Alice!
```

Wait a minute, where did Alice come from?

You have just witnessed an example of [Partial application](https://en.wikipedia.org/wiki/Partial_application).
In CE context, entries themselves may supply some (or all) default values for the actions that they define.
However, command line arguments always take precedence, so you can override any default value stored in the entry
(try the `say_hello Bob` example again).


Tweaking and saving
===================

Making changes to an existing entry
-----------------------------------

Suppose Alice has moved to a different country and we have to reflect this:
```
	ce bypath alice_entry \
	   tweak .country=Angola \
	   save
```

Cloning an entry with changes
-----------------------------

With the same tools it is very easy to clone an entry, make changes to it, and store under a different name:
```
	ce bypath alice_entry \
	   tweak .name=Bob .country=Belize \
	   save --entry_name=bob_entry
```


TODO: Stored entry vs in-memory object
--------------------------------------

TODO: add examples to access alice_entry::entry_name and alice_entry::entry_fs_path (since it is stored).
This data is dynamically added to in-memory loaded object, although it is deliberately missing from the stored entry.


Collections
===========

It is easy to work with `alice_entry` already, but accessing it by path is not very portable:
* *absolute paths* are not good, because they may change between systems
* *relative paths* are not good, because they depend on your current directory that may change.

It would be nice if our entries could be automatically found by a short name, whatever the current path.
To implement this, we introduce *collections*. A *collection* is just another type of entry (so is automatically a directory).
Being an entry, a *collection* contains:
* other entries (as subdirectories)
* own_parameters.json (which contains an index that is used to find other entries)
* own_methods.py (which contains methods for easy access to the component entries)

To simplify the interface, there is a default collection which lives in user's $HOME/working_collection directory.
CE system already knows about it, so searches in it by default.

Storing an entry in a collection
--------------------------------
```
	ce bypath alice_entry \
	   save --collection=~/working_collection
```
As the result, the whole entry will be recursively copied into *working_collection* directory,
and also registered in the *working_collection* index.

Lookup by name
--------------

Let's load our alice_entry from *working_collection* (byname does this by default) and ask the system where the entry came from:
```
	ce byname alice_entry \
	   tabulate _entry_name,_collection_fs_path,_entry_fs_path
alice_entry		/home/yourname/working_collection 	/home/yourname/working_collection/alice_entry
```

Lookup by a query
-----------------

One of the main advantages of storing entries in collections is a query-based lookup.
Any of the entry data fields can be used in such a query:
```
	ce find1 name=Alice \
	   tabulate name,family,country
Alice : Keymaker : Argentina
```

Lookups by query can sometimes return more or less than one result. To capture all the results we use **findN** action:
```
	ce findN family=Keymaker \
	   tabulate name,family,country
Alice : Keymaker : Argentina
Bob : Keymaker : Belize
```


---------

For OO-minded people an entry behaves like an instance of a class, on which you can access attributes or call methods. 
Entries can inherit both methods and data from other entries.
Having one entry it is very easy to extend it with a few extra attributes or methods and produce a derived entry.
