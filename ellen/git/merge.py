#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_repo
from ellen.utils.format import format_merge_result, format_index
from ellen.utils.git import make_git_env


class RepoMergeError(Exception):
    pass


class RepoPushError(Exception):
    pass


def _clone_and_fetch(from_repo, to_repo, worktree,
                     from_ref, to_ref, remote_name=None):
    tmp_repo = to_repo.clone(worktree, branch=to_ref, bare=False)

    if from_repo == to_repo:
        ref = 'origin/%s' % from_ref
    else:
        tmp_repo.add_remote(remote_name,
                            from_repo.path)
        ref = '%s/%s' % (remote_name, from_ref)
    # TODO: fetch remote_name
    tmp_repo.fetch_all()

    return tmp_repo, ref


def merge_flow(merger_name, merger_email,
               message_header, message_body, tmpdir,
               from_repo, to_repo, from_ref, to_ref,
               remote_name=None, no_ff=False,
               env_commiter_key='CODE_REMOTE_USER'):
    """merge with worktree(tmpdir)"""
    env = make_git_env(merger_name, merger_email)

    worktree = tmpdir
    merge_commit_sha = None
    try:
        tmp_repo, ref = _clone_and_fetch(from_repo, to_repo, worktree,
                                         from_ref, to_ref, remote_name)

        result = tmp_repo.merge(ref, message_header, message_body,
                                no_ff=no_ff, _env=env)
        if result['returncode'] != 0:
            raise RepoMergeError
        result = tmp_repo.push('origin', to_ref,
                               _env={env_commiter_key: merger_name})
        if result['returncode'] != 0:
            raise RepoPushError
        merge_commit_sha = to_repo.sha(to_ref)
    except RepoMergeError:
        pass
    except RepoPushError:
        pass
    return merge_commit_sha


def can_merge(tmpdir, from_repo, to_repo, from_ref, to_ref,
              remote_name=None):
    worktree = tmpdir

    tmp_repo, ref = _clone_and_fetch(from_repo, to_repo, worktree,
                                     from_ref, to_ref, remote_name)

    result = tmp_repo.merge_commits(to_ref, ref)

    if result and result['has_conflicts'] is False:
        return True
    else:
        return False


# FIXME: param _raise ??
def merge(repository, ref, msg='automerge', commit_msg='',
          no_ff=False, _raise=True, _env=None):
    # msg, commit_msg makes multiline commit message
    git = git_with_repo(repository)
    git_merge = git.bake('merge', ref, no_ff=no_ff)
    if msg:
        git_merge = git_merge.bake(m=msg)
    if commit_msg:
        git_merge = git_merge.bake(m=commit_msg)
    return git_merge(env=_env)


def merge_tree(repository, ours, theirs):
    theirs = repository.revparse_single(theirs)
    theirs_tree = theirs.tree
    ours = repository.revparse_single(ours)
    ours_tree = ours.tree
    merge_base = repository.merge_base(theirs.hex,
                                       ours.hex)
    merge_base_tree = repository.get(merge_base.hex).tree
    index = ours_tree.merge(theirs_tree, merge_base_tree)
    return format_index(index)


def merge_head(repository, ref):
    target = repository.revparse_single(ref)
    oid = target.oid
    merge_result = repository.merge(oid)
    return format_merge_result(merge_result)


def merge_commits(repository, ours, theirs):
    theirs = repository.revparse_single(theirs)
    ours = repository.revparse_single(ours)
    merge_index = repository.merge_commits(ours, theirs)
    return format_index(merge_index)
