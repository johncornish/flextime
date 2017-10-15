import click, os
from flextime import TaskTree
from flextime.interface import Add

@click.group()
@click.option('--datafile', '-f', default='tasks.yml')
@click.pass_context
def cli(ctx, datafile):
    ctx.obj = {'tasktree': TaskTree(datafile)}

@cli.command()
@click.argument('sort_keys', nargs=-1)
@click.option('--lim', default=5)
@click.pass_obj
def todo(ft, sort_keys, lim):
    def todo_str(todos):
        return "\n\n".join(['[{}] {}'.format(i, str(t)) for i, t in todos[:lim]])

    def show_todos():
        if len(sort_keys) > 0:
            todos = ft.multisorted(sort_keys)
        else:
            todos = ft.leaf_tuples()

        os.system('clear')
        print(todo_str(todos))
        
    while True:
        show_todos()
        cind = input("Complete [<i>/w/Q]: ")

        if cind.isdigit():
            ft.complete_task(int(cind))
        else:
            if cind == 'w':
                ft.save()
            break

@cli.command()
@click.argument('words', nargs=-1)
@click.pass_obj
def add(obj, words):
    a = Add(obj['tasktree'])
    c = ''
    while c != 'q':
        a.show_page()
        c = click.getchar()
        click.echo()
        
        if c.isdigit():
            a.select_key(c)
        elif c == 'n':
            a.next_page()
        elif c == 'p':
            a.prev_page()
        elif c == 'u':
            a.up_level()
        elif c == 'c':
            a.create()
        elif c == 'w':
            obj['tasktree'].save()
            break
