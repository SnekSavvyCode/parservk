from sqlalchemy.orm import mapped_column

class DynamicTableMeta(type):
	def __new__(meta, name, bases, namespace):
		if not "__tablename__" in namespace:
			raise ValueError("__tablename__ is required")
		if not len(bases): bases = (namespace.get("__custom_base__", Base),)
		for key, value in namespace.items():
			if not key.startswith('__'):
				namespace[key] = mapped_column(value.type, **value.params)
		cls = type(name, bases, namespace)

		return cls
