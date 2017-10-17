import click, os
import flextime
from flextime.interface import Show, Add

@click.group()
@click.option('--datafile', '-f', default='tasks.yml')
@click.pass_context
def cli(ctx, datafile):
    ctx.obj = {'tasktree': flextime.TaskTree(datafile)}

@cli.command()
@click.argument('sort_keys', nargs=-1)
@click.pass_obj
def show(obj, sort_keys):
    Show(obj['tasktree'], sort_keys).run()

@cli.command()
@click.argument('merge_files', nargs=-1)
@click.pass_obj
def add(obj, merge_files):
    Add(obj['tasktree'], merge_files).run()
