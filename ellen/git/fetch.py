#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_repo


def fetch_repository(repository, remote_name=None, is_q=False, env=None):
    git = git_with_repo(repository)

    if remote_name:
        git.fetch(remote_name)
    else:  # fetch all
        git.fetch(q=is_q, env=env)
