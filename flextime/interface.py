import click
import yaml

class Add:
    def __init__(self, tasktree):
        self._tasktree = tasktree
        self._path = []

        self.reset_offset()
        self.reset_keys()

    def reset_offset(self):
        self._page_offset = 0
        
    def reset_keys(self):
        self._keys = self._tasktree.keys_from_path(self._path)

    def select_key(self, key_index):
        key_index = int(key_index)
        if key_index < len(self._keys):
            key = self._keys[key_index]
        
            self._path.append(key)

            self.reset_offset()
            self.reset_keys()
        
    def has_prev_page(self):
        return self._page_offset > 0

    def has_next_page(self):
        num_keys = len(self._keys)
        return num_keys > (self._page_offset + 1) * 10

    def get_page(self):
        start = 0 + 10*self._page_offset
        end = 10 + 10*self._page_offset

        if start < len(self._keys):
            return self._keys[start:end]
        else:
            return self._keys
    
    def prev_page(self):
        if self.has_prev_page():
            self._page_offset -= 1

    def next_page(self):
        if self.has_next_page():
            self._page_offset += 1

    def up_level(self):
        if len(self._path) > 0:
            self._path.pop()
            
        self.reset_offset()
        self.reset_keys()

    def create(self):
        task_str = click.edit()
        if task_str is not None:
            data = yaml.safe_load(task_str)
            self._tasktree.merge_branch(self._path, data)
            self.reset_keys()

    def show_page(self):
        click.clear()
        for i, k in enumerate(self.get_page()):
            click.echo("[{}] {}".format(str(i), str(k)))

        click.echo()
        menu_line = '[u]p a level | [c]reate new task | [w]rite/quit | [q]uit'
        if self.has_prev_page():
            menu_line += ' | <[p]'

        if self.has_next_page():
            menu_line += ' | [n]>'
            
        click.echo(menu_line)
        click.echo('> ', nl=False)
