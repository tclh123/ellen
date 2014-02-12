# -*- coding: utf-8 -*-

import os

from _base import BareRepoTest, BARE_REPO_OTHER_BRANCH

from ellen.repo import Jagare
from ellen.utils.temp_repo import commit_something


class TestMerge(BareRepoTest):

    def _merge(self, no_ff):
        repo = Jagare(self.path)
        BR = 'br_test_merge'
        path = self.get_temp_path()

        # repo has work-tree
        repo.clone(path, branch=BARE_REPO_OTHER_BRANCH)
        repo = Jagare(os.path.join(path, '.git'))

        ret = repo.create_branch(BR, BARE_REPO_OTHER_BRANCH)
        assert ret
        sha1 = repo.sha(BARE_REPO_OTHER_BRANCH)

        commit_something(path, branch=BR)
        repo.update_head(BARE_REPO_OTHER_BRANCH)
        ret = repo.merge(BR, no_ff=no_ff)
        sha2 = repo.sha(BARE_REPO_OTHER_BRANCH)

        assert sha1 != sha2
        assert repo.sha(sha1) == sha1

    def test_merge(self):
        self._merge(no_ff=False)

    def test_merge_no_ff(self):
        self._merge(no_ff=True)

    def test_merge_tree(self):
        repo = Jagare(self.path)
        BR = 'br_test_merge'
        path = self.get_temp_path()

        # repo has work-tree
        repo.clone(path, branch=BARE_REPO_OTHER_BRANCH)
        repo = Jagare(os.path.join(path, '.git'))

        ret = repo.create_branch(BR, BARE_REPO_OTHER_BRANCH)
        assert ret

        commit_something(path, branch=BR)
        repo.update_head(BARE_REPO_OTHER_BRANCH)
        index = repo.merge_tree(repo.head.target.hex, BR)
        assert index['has_conflicts'] == False

    def test_merge_head(self):
        repo = Jagare(self.path)
        BR = 'br_test_merge'
        path = self.get_temp_path()

        # repo has work-tree
        repo.clone(path, branch=BARE_REPO_OTHER_BRANCH)
        repo = Jagare(os.path.join(path, '.git'))

        ret = repo.create_branch(BR, BARE_REPO_OTHER_BRANCH)
        assert ret

        commit_something(path, branch=BR)
        repo.update_head(BARE_REPO_OTHER_BRANCH)
        merge_result = repo.merge_head(BR)
        assert merge_result['is_fastforward']

    def test_merge_commits(self):
        repo = Jagare(self.path)
        BR = 'br_test_merge'
        path = self.get_temp_path()

        # repo has work-tree
        repo.clone(path, branch=BARE_REPO_OTHER_BRANCH)
        repo = Jagare(os.path.join(path, '.git'))

        ret = repo.create_branch(BR, BARE_REPO_OTHER_BRANCH)
        assert ret

        commit_something(path, branch=BR)
        repo.update_head(BARE_REPO_OTHER_BRANCH)
        merge_index = repo.merge_commits(repo.head.target.hex, BR)
        assert merge_index['has_conflicts'] is False

    def test_merge_flow(self):
        repo = Jagare(self.path)
        BR = 'br_test_merge'
        sha1 = repo.sha(BARE_REPO_OTHER_BRANCH)

        from_repo_path = self.get_temp_path()
        from_repo = repo.clone(from_repo_path, branch=BARE_REPO_OTHER_BRANCH,
                               bare=True)
        ret = from_repo.create_branch(BR, BARE_REPO_OTHER_BRANCH)
        assert ret
        commit_something(from_repo_path, branch=BR)

        tmpdir = self.get_temp_path()

        # different repo
        sha = repo.merge_flow('lh', 'lh@xxx.com',
                              'test_header', 'test_body', tmpdir,
                              from_repo_path, BR, BARE_REPO_OTHER_BRANCH,
                              remote_name='hub/xxxproject', no_ff=True)
        assert sha

        sha2 = repo.sha(BARE_REPO_OTHER_BRANCH)

        assert sha1 != sha2
        assert repo.sha(sha1) == sha1

        # same repo
        tmpdir2 = self.get_temp_path()
        from_sha1 = from_repo.sha(BARE_REPO_OTHER_BRANCH)
        assert from_sha1 == sha1
        sha = from_repo.merge_flow('lh', 'lh@xxx.com',
                                   'test_header', 'test_body', tmpdir2,
                                   from_repo_path, BR, BARE_REPO_OTHER_BRANCH,
                                   no_ff=True)
        assert sha
        from_sha2 = from_repo.sha(BARE_REPO_OTHER_BRANCH)
        assert from_sha1 != from_sha2
        assert from_repo.sha(from_sha1) == from_sha1

    def test_can_merge(self):
        repo = Jagare(self.path)
        BR = 'br_test_merge'

        from_repo_path = self.get_temp_path()
        from_repo = repo.clone(from_repo_path, branch=BARE_REPO_OTHER_BRANCH,
                               bare=True)
        ret = from_repo.create_branch(BR, BARE_REPO_OTHER_BRANCH)
        assert ret
        commit_something(from_repo_path, branch=BR)

        tmpdir = self.get_temp_path()

        ret = repo.can_merge(tmpdir,
                             from_repo_path, BR, BARE_REPO_OTHER_BRANCH,
                             remote_name='hub/xxxproject')
        assert ret is True
