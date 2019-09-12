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


Let's now add data to the same entry:
```
	echo '{ "name": "Alice", "family": "Keymaker", "phone": "123-456-789", "country": "Argentina" }' > alice_entry/own_parameters.json
```

Again, we can access this data straight away using the existing infrastructure:
```
	ce bypath alice_entry \
	   tabulate name
Alice

	ce bypath alice_entry \
	   tabulate name,country,phone --separator ' : '
Alice : Argentina : 123-456-789
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
However command line arguments always take precedence, so you can override any default value stored in the entry.

----------

For OO-minded people an entry behaves like an instance of a class, on which you can access attributes or call methods. 
Entries can inherit both methods and data from other entries.
Having one entry it is very easy to extend it with a few extra attributes or methods and produce a derived entry.
