
# 传入git地址和git凭据，获取所有分支
from git.repo import Repo
import os, shutil

git_repo = "https://gitee.com/openspug/spug"
git_credential = ""
clone_dir = os.path.join(os.getcwd(), 'test')

if os.path.exists(clone_dir):
    shutil.rmtree(clone_dir)

Repo.clone_from(git_repo, to_path=clone_dir)
# 获取分支
repo = Repo(clone_dir)
branch = []
# print(repo.remote().refs)
# print(repo.references)
for ref in repo.remote().refs:
    if ref.remote_head != 'HEAD':
        branch.append(ref.remote_head)

if __name__ == '__main__':
    pass