import importlib
import traceback

try:
    importlib.invalidate_caches()
    m = importlib.import_module('app.main')
    names = [n for n in dir(m) if not n.startswith('__')]
    print('Imported app.main successfully.')
    print('Available names:', names)
except Exception:
    traceback.print_exc()