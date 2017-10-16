import click
import yaml

class Menu:
    def __init__(self, pagify=True, input_type='char'):
        self._exit = False

        self.pagify = pagify
        self.input_type = input_type
        self.items = []
        self.page_offset = 0
        self.char_options = {
            'q': ('[q]uit', self.set_quit),
            #'n': ('[n]ext page', self.next_page, self.has_next_page),
            'n': ('[n]ext page', self.next_page, lambda: True),
            'p': ('[p]rev page', self.prev_page, self.has_prev_page),
        }
        self.char_option_display = ['qw', 'pn']
        self.cond_options = [(lambda x: x.isdigit(), self.select_item)]

    def run(self):
        while not self._exit:
            click.echo(self.option_str())
            click.echo(self.item_str())
            click.echo('> ', nl=False)
            if self.input_type == 'char':
                self.handle_option(click.getchar())
                click.echo()
            else:
                self.handle_option(input())
                
    def handle_option(self, choice):
        if choice in self.char_options:
            self.char_options[choice][1](choice)
        else:
            for o in self.cond_options:
                check, f = o
                if check(o):
                    f(o)
            
    def reset_offset(self):
        self.page_offset = 0

    def set_quit(self, *args):
        self._exit = True

    def select_item(self, page_item_index):
        pass
       
    def has_prev_page(self):
        return self.page_offset > 0

    def has_next_page(self):
        num_items = len(self.items)
        return num_items > (self.page_offset + 1) * 10

    def get_page_items(self):
        start = 0 + 10*self.page_offset
        end = 10 + 10*self.page_offset

        if start < len(self.items):
            return self.items[start:end]
        else:
            return self.items

    def option_str(self):
        def option_to_str(o):
            if o in self.char_options:
                display_str, f, *rest = self.char_options[o]
                if len(rest) > 0 and not rest[0]():
                    return ''
                return display_str
            else:
                return ''
            
        strs = list(map(lambda s: list(map(option_to_str, s)), self.char_option_display))
        if len(strs) == 0:
            strs = [list(map(option_to_str, self.char_options.values()))]

        return '\n'.join([
            ' | '.join(filter(lambda s: s, line)) for line in filter(any, strs)
        ])
                
    def item_str(self):
        items = self.get_page_items() if self.pagify else self.items
        return "\n".join(["[{}] {}".format(i, item) for i, item in enumerate(items)])
    
    def prev_page(self, *args):
        if self.has_prev_page():
            self.page_offset -= 1

    def next_page(self, *args):
        if self.has_next_page():
            self.page_offset += 1

class Add(Menu):
    def __init__(self, tasktree, **kwargs):
        super(Add, self).__init__(**kwargs)
        self._tasktree = tasktree

        self.reset_items()

    def reset_items(self):
        self.items = self._tasktree.keys_from_path(self._path)
        
    def select_item(self, page_item_index):
        key_index = int(key_index) + self._page_offset*10
        if key_index < len(self._keys):
            key = self._keys[key_index]
        
            self._path.append(key)

            self.reset_offset()
            self.reset_keys()
 
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
