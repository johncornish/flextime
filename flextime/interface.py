import click
import yaml
import flextime

from datetime import date
from functools import reduce

class Menu:
    def __init__(self, tasktree, pagify=True, input_type='char'):
        self._exit = False

        self._tasktree = tasktree
        self.pagify = pagify
        self.input_type = input_type
        self._items = []
        self.page_offset = 0
        self.char_options = {
            'q': ('[q]uit', self.set_quit),
            'w': ('[w]rite/quit', self.write_quit),
            'n': ('[n]ext page', self.next_page, self.has_next_page),
            'p': ('[p]rev page', self.prev_page, self.has_prev_page),
        }
        self.char_option_display = ['qw', 'pn']
        self.cond_options = [(lambda x: x.isdigit(), self.select_item)]

    def run(self):
        while not self._exit:
            click.clear()
            click.echo(self.option_str())
            click.echo()
            click.echo(self.item_str())
            click.echo('> ', nl=False)
            if self.input_type == 'char':
                self.handle_option(click.getchar())
                click.echo()
            else:
                self.handle_option(input())

    def write_quit(self, *args):
        self._tasktree.save()
        self.set_quit()
                
    def handle_option(self, choice):
        if choice in self.char_options:
            name, f, *rest = self.char_options[choice]
            if len(rest) == 0 or (len(rest) > 0 and rest[0]()):
                f(choice)
                
        else:
            for o in self.cond_options:
                check, f = o
                if check(choice):
                    f(choice)
            
    def reset_offset(self):
        self.page_offset = 0

    def set_quit(self, *args):
        self._exit = True

    def select_item(self, page_item_index):
        pass
       
    def has_prev_page(self):
        return self.page_offset > 0

    def has_next_page(self):
        num_items = len(self._items)
        return num_items > (self.page_offset + 1) * 10

    def get_item(self, page_item_index):
        if self.pagify:
            item_index = int(page_item_index) + self.page_offset*10
        else:
            item_index = int(page_item_index)

        if item_index < len(self._items):
            return self._items[item_index]
        else:
            return False

        
    def get_page_items(self):
        start = 0 + 10*self.page_offset
        end = 10 + 10*self.page_offset

        if start < len(self._items):
            return self._items[start:end]
        else:
            return self._items

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
        items = self.get_page_items() if self.pagify else self._items
        return "\n".join(["[{}] {}".format(i, str(item)) for i, item in enumerate(items)])
    
    def prev_page(self, *args):
        if self.has_prev_page():
            self.page_offset -= 1

    def next_page(self, *args):
        if self.has_next_page():
            self.page_offset += 1

class Add(Menu):
    def __init__(self, tasktree, path, merge_files, **kwargs):
        super(Add, self).__init__(tasktree, **kwargs)
        self.char_options.update({
            'a': ('easy [a]dd', self.add_interactive),
            'y': ('edit [y]aml', self.edit_yaml),
            'm': ('[m]erge files at current path', self.merge_files, self.merge_files_present),
            'u': ('[u]p a level', self.up_level),
        })

        self.char_option_display = [
            'qwaym',
            'upn',
        ]

        self._merge_files = merge_files
        self._path = flextime.utils.guess_path(tasktree.tree(), path) if len(path) > 0 else []
        self.reset_items()

    def merge_files_present(self):
       return len(self._merge_files) > 0

    def merge_files(self, *args):
        if self.merge_files_present():
            merger = reduce(
                lambda acc, f: {**acc, **flextime.TaskTree.file_to_dict(f)},
                self._merge_files,
                {}
            )

            click.echo('Current tree:')
            click.echo(flextime.TaskTree.dump_dict(self._tasktree.branch_from_path(self._path)))
            click.echo('Tree from files:')
            click.echo(flextime.TaskTree.dump_dict(merger))

            if click.confirm('Really merge?'):
                self._tasktree.merge_branch(self._path, merger)
                self._merge_files = []
                self.reset_items()

    def option_str(self):
        return "Path: {}\n{}".format(' > '.join(self._path), super(Add, self).option_str())
        
    def reset_items(self):
        self._items = self._tasktree.keys_from_path(self._path)
        
    def select_item(self, page_item_index):
        item = self.get_item(page_item_index)
        
        if item:
            self._path.append(item)
            self.reset_offset()
            self.reset_items()
 
    def up_level(self, *args):
        if len(self._path) > 0:
            self._path.pop()
            
        self.reset_offset()
        self.reset_items()

    def add_interactive(self, *args):
        click.echo()
        title = click.prompt('Task name', default='cancel')
        if title != 'cancel':
            due = click.prompt('Due date', default='none')
            time = click.prompt('Estimated time', default='none')
            new_branch = {title: {}}

            if due != 'none':
                new_branch[title]['_d'] = due

            if time != 'none':
                new_branch[title]['_t'] = time

            self._tasktree.merge_branch(self._path, new_branch)
            self.reset_items()
        
    def edit_yaml(self, *args):
        task_str = click.edit(flextime.TaskTree.dump_dict(self._tasktree.branch_from_path(self._path)))
        if task_str is not None:
            data = yaml.safe_load(task_str)
            self._tasktree.merge_branch(self._path, data)
            self.reset_items()
    
class Show(Menu):
    def __init__(self, tasktree, sort_keys, **kwargs):
        super(Show, self).__init__(tasktree, **kwargs)
        self.char_option_display = [
            'qw',
            'pn',
        ]

        self._sort_keys = sort_keys
        self.reset_items()

    def reset_items(self):
        self._items = self._tasktree.sorted_leaves(self._sort_keys)
        
    def select_item(self, page_item_index):
        leaf = self.get_item(page_item_index)
        
        if leaf:
            self._tasktree.delete_branch(leaf.path)
            self.reset_items()
