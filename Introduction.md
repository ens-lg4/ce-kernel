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

```
	mkdir alice_entry
	echo '{ "name": "Alice", "family": "Keymaker", "phone": "123-456-789", "country": "Argentina" }' > alice_entry/own_parameters.json
```
We have created an entry that contains some data about Alice, and we can access it straight away
using the existing infrastructure. Here is how we can read formatted data out of it:
```
	ce bypath alice_entry \
	   tabulate name
Alice

	ce bypath alice_entry \
	   tabulate name,phone --separator ' : '
Alice : Atlanta : 123-456-789
```

We shall return to the structure of the command line interface later,
but for now let's just note two commonplace actions in the example above:
* "bypath" means loading an entry from the filesystem and
* "tabulate" means displaying a subset of the data

We can also create an action specific to our new entry:
```

	cat <<EOF >alice_entry/own_methods.py
	def say_hello(name):
		print("Hello, "+name+"!")
	EOF
```

And run it. Since it requires a parameter, we supply it from the command line:
```

	ce bypath alice_entry \
	   say_hello Bob
Hello, Bob!
```

What happens if we omit this parameter?
```

	ce bypath alice_entry \
	   say_hello
Hello, Alice!
```

Wait, where did Alice come from?


----------

For OO-minded people an entry behaves like an instance of a class, on which you can access attributes or call methods. 
Entries can inherit both methods and data from other entries.
Having one entry it is very easy to extend it with a few extra attributes or methods and produce a derived entry.
