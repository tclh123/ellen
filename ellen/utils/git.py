#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import


from pygit2 import (GIT_OBJ_TAG, GIT_OBJ_BLOB,
                    GIT_OBJ_TREE, GIT_OBJ_COMMIT)


PYGIT2_OBJ_TYPE = {
    GIT_OBJ_COMMIT: 'commit',
    GIT_OBJ_BLOB: 'blob',
    GIT_OBJ_TREE: 'tree',
    GIT_OBJ_TAG: 'tag',
}


# TODO: should be git rev-parse command.  e.g. repo.rev_parse

def resolve_version(repository, version):
    '''返回完整的 40 位的 commit hash '''
    try:
        obj = repository.revparse_single(version)
        if obj.type == GIT_OBJ_TAG:
            commit = repository[obj.target]
        elif obj.type == GIT_OBJ_COMMIT:
            commit = obj
        elif obj.type == GIT_OBJ_BLOB:
            return None
        elif obj.type == GIT_OBJ_TREE:
            return None
    except KeyError:
        return None
    except ValueError:
        return None
    return commit.hex


def resolve_type(repository, version):
    try:
        obj = repository.revparse_single(version)
        type = PYGIT2_OBJ_TYPE[obj.type]
    except KeyError:
        type = None
    return type


def make_git_env(username=None, email=None, is_anonymous=False):
    env = {}
    if is_anonymous:
        env['GIT_AUTHOR_NAME'] = 'anonymous'
        env['GIT_AUTHOR_EMAIL'] = 'anonymous@douban.com'
        env['GIT_COMMITTER_NAME'] = 'anonymous'
        env['GIT_COMMITTER_EMAIL'] = 'anonymous@douban.com'
    else:
        env['GIT_AUTHOR_NAME'] = username
        env['GIT_AUTHOR_EMAIL'] = email
        env['GIT_COMMITTER_NAME'] = username
        env['GIT_COMMITTER_EMAIL'] = email
    return env
