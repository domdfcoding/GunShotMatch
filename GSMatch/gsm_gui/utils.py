def collapse_label(text, collapsed=True):
	import sys
	if sys.platform == "win32":
		return f"{text} {'>>' if collapsed else '<<'}"
	else:
		return f"{'⯈' if collapsed else '⯆'} {text}"
