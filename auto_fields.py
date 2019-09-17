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
			return self.own_methods[name]
		except KeyError:
			raise AttributeError(name)

	def __setattr__(self, name, value):
		self.own_methods[name] = value

	def can(self, name):
		return name in self.own_methods

	def __getitem__(self, name):
		return self.own_params[name]

	def __setitem__(self, name, value):
		self.own_params[name] = value

	def get(self, name, def_value=None):
		try:
			return self.own_params[name]
		except KeyError:
			return def_value


if __name__ == '__main__':

	foo = Entry( own_methods={
		'hi': lambda x='Mum' : "Hello, " + x
	})

	print(foo.can('hi'))
	print(foo.hi('Lenny'))
	print("")

	print(foo.can('bye'))
	try:
		foo.bye()
	except AttributeError as e:
		print("Missing method for {}()".format(e))
	print("")

	foo.bye = lambda x='Dad' : "Goodbye, " + x
	print(foo.can('bye'))
	print(foo.bye())

	print('-' * 40)
	bar = Entry({'erste': 10, 'dritte': 30})

	print(bar['erste'])
	zw = bar.get('zweite', 'default-for-zweite')
	print(zw)
	try:
		zw = bar['zweite']
	except KeyError as e:
		print("Missing value for {}".format(e))
	print(bar['dritte'])

	bar['zweite'] = 200
	bar['dritte'] = 300

	print(bar['zweite'])
	print(bar['dritte'])
