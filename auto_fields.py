#!/usr/bin/env python3

"""
	This is a demonstration of how to redefine both object.attribute and object["key"] notation in a class.

	For CE the two types of access could differentiate between data attributes and methods (traditional),
	or between "own" and "effective" (inherited) attributes (mixing access to data with access to methods).

	To be decided...
"""

class Entry(object):
	def __init__(self, own_params={}, own_methods={}):
		super(self.__class__, self).__setattr__('own_params', own_params)
		super(self.__class__, self).__setattr__('own_methods', own_methods)
	
		print( "Creating an Entry({}, {})".format(own_params, own_methods) )

	def __getattr__(self, name):
		try:
			return self.own_params[name]
		except KeyError:
			try:
				return self.own_methods[name]
			except KeyError:
				print("missing-value-or-method-for-"+name)
				return None

	def __setattr__(self, name, value):
		if callable(value):
			self.own_methods[name] = value
		else:
			self.own_params[name] = value

	def __getitem__(self, name):
		try:
			return self.own_params[name]
		except KeyError:
			return "missing-value-for-"+name

	def __setitem__(self, name, value):
		self.own_params[name] = value



foo = Entry({'alpha': 5}, {
	'hi': lambda x='Mum' : "Hello, " + x
})

print(foo['alpha'])
print(foo.beta)
print(foo.hi('Lenny'))
print(foo.bye)

foo.bye = lambda x='Dad' : "Goodbye, " + x

print(foo.bye())


bar = Entry({'erste': 1, 'dritte': 3})

print(bar.erste)
print(bar.zweite)
print(bar.dritte)

bar.zweite = 20
bar['dritte'] = 30

print(bar['zweite'])
print(bar['dritte'])
