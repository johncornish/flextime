import click, os
import flextime
from flextime.interface import List, Add

@click.group()
@click.option('--datafile', '-f', default='tasks.yml')
@click.pass_context
def cli(ctx, datafile):
    ctx.obj = {'tasktree': flextime.TaskTree(datafile)}

@cli.command()
@click.argument('sort_keys', nargs=-1)
@click.pass_obj
def list(obj, sort_keys):
    List(obj['tasktree'], sort_keys).run()

@cli.command()
@click.argument('path', nargs=-1)
@click.option('-m', '--merge-files', multiple=True)
@click.pass_obj
def add(obj, path, merge_files):
    Add(obj['tasktree'], path, merge_files).run()

@cli.command()
@click.argument('schedule_file', default='schedule.yml')
@click.pass_obj
def show(obj, schedule_file):
    s = flextime.Scheduler(obj['tasktree'], schedule_file)
    unscheduled, tbs = s.scheduled_tasks()
    
    if len(unscheduled) > 0:
        print('Unscheduled tasks:')
        print('\t{}\n'.format('\n\t'.join([str(task) for task in unscheduled])))

    for t in tbs:
        print(str(t))
