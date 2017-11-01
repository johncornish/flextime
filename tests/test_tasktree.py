import pytest

from flextime import TaskTree, utils

def new_tree():
    initial_data = {
        'k1': {
            'k2': {
                '_t': 30,
            }
        },
        'k3': {
            '_t': 25
        }
    }

    t = TaskTree()
    t._datatree = {}
    t.merge_branch([], initial_data)

    return t

def test_merge_branch():
    new_data = {'k4': {'_t': 20}}

    after_merge = {
        'k2': {
            '_t': 30,
        },
        'k4': {
            '_t': 20
        }
    }

    t = new_tree()
    t.merge_branch(['k1'], new_data)

    assert t.branch_from_path(['k1']) == after_merge

def test_delete_branch():
    after_delete = {
        'k1': {},
        'k3': {
            '_t': 25
        }
    }

    t = new_tree()
    t.delete_branch(['k1', 'k2'])

    assert t.branch_from_path([]) == after_delete

def test_replace_branch():
    after_replace = {
        'k4': {
            '_t': 60
        }
    }
    
    t = new_tree()
    t.replace_branch([], after_replace)

    assert t.branch_from_path([]) == after_replace

    t = new_tree()
    t.replace_branch(['k3'], after_replace)

    assert t.branch_from_path(['k3']) == after_replace
