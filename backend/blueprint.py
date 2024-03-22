# blueprint.py purchase purchase_order
import os, sys
from shutil import copy2, copytree

"""
"""

if __name__ == "__main__":
    """
    Указываешь сначала сервис, потом имя модели Пример | blueprint.py purchase purchase_order
    """
    print(sys.argv)
    app = sys.argv[1]
    model = sys.argv[2]
    path = f'app/{app}'
    copytree('core/blueprint', path)
    for root, dirs, files in os.walk(path):
        print(root, dirs, files)
        for filename in files:
            replace_name = filename
            if filename != '__init__.py':

                new_filename = f'{model}_{filename}'
                original_path = os.path.join(root, filename)
                new_path = os.path.join(root, new_filename)
                if not os.path.exists(new_path):
                    os.rename(original_path, new_path)
                replace_name = new_filename
            f = open(os.path.join(root, replace_name), 'r')
            filedata = f.read()
            f.close()
            newdata = filedata.replace("new_service", app)
            newdata = newdata.replace("blueprint", model)
            newdata = newdata.replace("blueprint".capitalize(), model.capitalize())
            f = open(os.path.join(root, replace_name), 'w')
            f.write(newdata)
            f.close()
    os.rename(f'{path}/module', f'{path}/{model}')