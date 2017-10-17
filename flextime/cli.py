import click, os
from flextime import TaskTree
from flextime.interface import Show, Add

@click.group()
@click.option('--datafile', '-f', default='tasks.yml')
@click.pass_context
def cli(ctx, datafile):
    ctx.obj = {'tasktree': TaskTree(datafile)}

@cli.command()
@click.argument('sort_keys', nargs=-1)
@click.pass_obj
def show(obj, sort_keys):
    Show(obj['tasktree'], sort_keys).run()

@cli.command()
@click.argument('words', nargs=-1)
@click.pass_obj
def add(obj, words):
    Add(obj['tasktree']).run()
