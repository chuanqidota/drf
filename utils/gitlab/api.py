import gitlab

"""
认证与连接
连接到 GitLab 实例
使用个人访问令牌进行认证

项目操作
获取项目列表
获取单个项目
创建项目
删除项目
编辑项目信息

分支操作
获取分支列表
创建分支
删除分支
保护分支
取消保护分支
合并分支

标签操作
获取标签列表
创建标签
删除标签

合并请求操作
获取合并请求列表
获取单个合并请求
创建合并请求
关闭合并请求
接受合并请求
合并合并请求
拒绝合并请求

问题操作
获取问题列表
获取单个问题
创建问题
关闭问题
编辑问题

成员操作
获取项目成员列表
添加项目成员
删除项目成员
更改项目成员权限

组操作
获取组列表
获取单个组
创建组
删除组
编辑组信息
添加组成员
删除组成员
更改组成员权限

文件操作
上传文件
下载文件
删除文件
编辑文件内容
"""


class GitLabManager:
    def __init__(self, url, private_token):
        """
            初始化
        :param url: url地址
        :param private_token: token
        """
        # self.gitlab = gitlab.Gitlab(url, private_token, ssl_verify=True)
        self.gitlab = gitlab.Gitlab(url, private_token)

    @staticmethod
    def object_to_dict(obj):
        """
            把对象转字典
        :param obj:
        :return:
        """
        return {attr: getattr(obj, attr) for attr in dir(obj) if not attr.startswith('__')}

    def create_group(self, name, path, description=None):
        """
            组操作>创建分组
        :param name: 分组的名称可以和path一致
        :param path: 路径
        :param description: 分组描述
        :return:
        """
        try:
            group = self.gitlab.groups.create({
                "name": name,
                "path": path,
                "description": description,
            })
            return group
        except gitlab.exceptions.GitlabCreateError as e:
            print(f"Error creating group: {e}")
            return None

    def list_groups(self):
        """
            组操作>获取组列表
        :return:
        """
        return self.gitlab.groups.list(all=True)

    def get_group(self, group_id):
        """
            组操作>获取单个组
        :param group_id: 组id
        :return:
        """
        try:
            group = self.gitlab.groups.get(group_id)
            return group
        except gitlab.exceptions.GitlabGetError as e:
            print(f"Error getting group details: {e}")
            return None

    def update_group(self, group_id, name=None, path=None, description=None):
        """
            修改已有组的属性
        :param group_id:
        :param name:
        :param path:
        :param description:
        :return:
        """
        group = self.get_group_details(group_id)
        if group:
            try:
                updated_group = group.edit({
                    "name": name or group.name,
                    "path": path or group.path,
                    "description": description or group.description,
                })
                return updated_group is not None
            except gitlab.exceptions.GitlabUpdateError as e:
                print(f"Error updating group: {e}")
                return False
        else:
            return False

    def manage_group_members(self, group_id, user_id, access_level, action):
        """
            管理组成员：添加、移除或更新成员的角色权限
        :param group_id:
        :param user_id:
        :param access_level:
        :param action:
        :return:
        """
        group = self.retrieve_group(group_id)
        if group:
            if action == "add":
                try:
                    group.members.create({"user_id": user_id, "access_level": access_level})
                    print(f"User {user_id} added to group {group_id} with access level {access_level}.")
                except gitlab.exceptions.GitlabCreateError as e:
                    print(f"Error adding member: {e}")
            elif action == "remove":
                try:
                    group.members.delete(user_id)
                    print(f"User {user_id} removed from group {group_id}.")
                except gitlab.exceptions.GitlabDeleteError as e:
                    print(f"Error removing member: {e}")
            elif action == "update":
                try:
                    group.members.update(user_id, {"access_level": access_level})
                    print(f"Access level for user {user_id} in group {group_id} updated to {access_level}.")
                except gitlab.exceptions.GitlabUpdateError as e:
                    print(f"Error updating member access level: {e}")
            else:
                print(f"Invalid action '{action}'. Supported actions are 'add', 'remove', and 'update'.")
        else:
            print(f"Group {group_id} not found.")

    def delete_group_member(self, group_id, user_id):
        pass

    def change_group_member_access(self, group_id, user_id, access_level):
        """

        :param group_id:
        :param user_id:
        :param access_level:
        :return:
        """
        pass

    def list_group_members(self, group_id):
        """
            获取指定组的所有成员
        :param group_id: 组id
        :return:
        """
        pass

    def add_group_members(self, group_id, user_id, access_level):
        pass

    def delete_group_members(self, group_id, user_id):
        pass

    def change_group_members_access(self, group_id, user_id, access_level):
        """

        :param group_id:
        :param user_id:
        :param access_level:
        :return:
        """
        pass

    def get_user_info(self, user_id):
        """
            获取指定ID用户的详细信息
        :param user_id: 用户id
        :return:
        """
        return self.gitlab.users.get(user_id)

    def create_project(self, name, description, visibility="private"):
        """
            创建新项目
        :param name: 项目名称
        :param description: 描述
        :param visibility: 可见行 private / public
        :return:
        """
        return self.gitlab.projects.create({"name": name, "description": description, "visibility": visibility})

    def update_project(self, name, description, visibility="private"):
        pass

    def list_projects(self):
        """
            列出所有可访问的项目
        :return:
        """
        """
        # 获取项目。默认获取第一页的项目，每页20个
        projects = self.gitlab.projects.list()

        # 获取指定页的项目
        projects = self.gitlab.projects.list(page=2)

        # 获取所有项目
        projects = self.gitlab.projects.list(all=True)

        # 根据项目名称搜索项目
        projects = self.gitlab.projects.list(search='project_name')

        # 获取archived项目
        projects = self.gitlab.projects.list(archived=1)

        # 根据项目visibility获取项目，public,internal,private
        projects = self.gitlab.projects.list(visibility='public')

        # 获取当前用户（token的账户）拥有的项目
        projects = self.gitlab.projects.list(owned=True)

        # 获取当前用户（token的账户）启动的项目
        projects = self.gitlab.projects.list(starred=True)

        # 搜索结果排序
        # 在不指定的排序标准的情况下默认按照created_at,desc降序排列
        # order_by参数：id, name, path, created_at, updated_at, last_activity_at.
        # sort参数:asc,desc.
        # 查找所有项目，并按照项目id升序排列
        projects = self.gitlab.projects.list(all=True, order_by='id', sort="asc")
        """
        return self.gitlab.projects.list(owned=True)

    def get_project(self, project_id):
        """
            通过ID获取项目
        :param project_id: 项目id
        :return:
        """
        return self.gitlab.projects.get(project_id)

    def delete_project(self, project_id):
        """
            删除项目
        :param project_id: 项目id
        :return:
        """
        project = self.get_project(project_id)
        project.delete()

    def create_branch(self, project_id, branch_name, ref):
        """
            在指定项目中创建新分支
        :param project_id: 项目id
        :param branch_name: 项目名称
        :param ref: 参考那个分支
        :return:
        """
        project = self.get_project(project_id)
        if project:
            return project.branches.create({"branch": branch_name, "ref": ref})
        else:
            return None

    def list_branches(self, project_id):
        """
            列出指定项目的所有分支
        :param project_id: 项目id
        :return:
        """
        project = self.get_project(project_id)
        if project:
            return [branch.name for branch in project.branches.list()]
        else:
            return []

    def delete_branch(self, project_id, branch_name):
        """
            删除分支
        :param project_id:
        :param branch_name:
        :return:
        """
        project = self.get_project(project_id)
        project.branches.delete(branch_name)

    def protect_branch(self, project_id, branch_name,
                       push_access_levels=None,
                       merge_access_levels=None,
                       unprotect_access_levels=None, code_owner_approval_required=False,
                       approvals_required=None, approval_rules=None):
        """
            为项目中的分支设置保护规则
        :param project_id:
        :param branch_name:
        :param push_access_levels:
        :param merge_access_levels:
        :param unprotect_access_levels:
        :param code_owner_approval_required:
        :param approvals_required:
        :param approval_rules:
        :return:
        """
        project = self.get_project(project_id)
        if project:
            try:
                project.protectedbranches.create({
                    "name": branch_name,
                    "push_access_levels": push_access_levels or [],
                    "merge_access_levels": merge_access_levels or [],
                    "unprotect_access_levels": unprotect_access_levels or [],
                    "code_owner_approval_required": code_owner_approval_required,
                    "approvals_required": approvals_required,
                    "approval_rules": approval_rules or [],
                })
                return True
            except gitlab.exceptions.GitlabCreateError as e:
                print(f"Error protecting branch: {e}")
                return False
        else:
            return False

    def delete_protected_branch(self, project_id, branch_name):
        """
            把保护分支删除
        :param project_id:
        :param branch_name:
        :return:
        """
        project = self.get_project(project_id)
        protected_branch = project.protectedbranches.get(branch_name)
        protected_branch.delete()

    def get_protected_branch(self, project_id, branch_name):
        """
            获取指定分支的保护规则
        :param project_id:
        :param branch_name:
        :return:
        """
        project = self.get_project(project_id)
        if project:
            try:
                protected_branch = project.protectedbranches.get(branch_name)
                return protected_branch
            except gitlab.exceptions.GitlabGetError as e:
                print(f"Error getting protected branch: {e}")
                return None
        else:
            return None

    def update_protected_branch(self, project_id, branch_name, push_access_levels=None,
                                merge_access_levels=None,
                                unprotect_access_levels=None,
                                code_owner_approval_required=None,
                                approvals_required=None,
                                approval_rules=None):
        """
            修改已有分支的保护规则
        :param project_id:
        :param branch_name:
        :param push_access_levels:
        :param merge_access_levels:
        :param unprotect_access_levels:
        :param code_owner_approval_required:
        :param approvals_required:
        :param approval_rules:
        :return:
        """
        protected_branch = self.get_protected_branch(project_id, branch_name)
        if protected_branch:
            try:
                updated_branch = protected_branch.update({
                    "push_access_levels": push_access_levels or protected_branch.push_access_levels,
                    "merge_access_levels": merge_access_levels or protected_branch.merge_access_levels,
                    "unprotect_access_levels": unprotect_access_levels or protected_branch.unprotect_access_levels,
                    "code_owner_approval_required": code_owner_approval_required or protected_branch.code_owner_approval_required,
                    "approvals_required": approvals_required or protected_branch.approvals_required,
                    "approval_rules": approval_rules or protected_branch.approval_rules,
                })
                return updated_branch is not None
            except gitlab.exceptions.GitlabUpdateError as e:
                print(f"Error updating protected branch: {e}")
                return False
        else:
            return False

    def list_merge_requests(self, project_id, state="opened"):
        """
            列出指定项目中处于特定状态（默认为打开状态）的合并请求
        :param project_id: 项目id
        :param state:
        :return:
            返回的是对象 iid是项目merge的id
        """
        project = self.get_project(project_id)
        if project:
            return project.mergerequests.list(state=state)
        else:
            return []

    def create_merge_request(self, project_id, source_branch, target_branch, title, description=None):
        """
            在指定项目中创建新的合并请求,这里存在失败的可能,需要特殊处理
        :param project_id: 项目id
        :param source_branch: 源分支
        :param target_branch: 目的分支
        :param title: 标题
        :param description: 描述
        :return:
            对象可以通过点出来
            {'id': 297344392, 'iid': 1, 'project_id': 57091227, 'title': 'title-test', 'description': 'description-test', 'state': 'opened', 'created_at': '2024-04-22T03:19:17.365Z', 'updated_at': '2024-04-22T03:19:17.365Z', 'merged_by': None, 'merge_user': None, 'merged_at': None, 'closed_by': None, 'closed_at': None, 'target_branch': 'master', 'source_branch': 'dev', 'user_notes_count': 0, 'upvotes': 0, 'downvotes': 0, 'author': {'id': 8730526, 'username': 'chuanqidota', 'name': 'chuanqidota', 'state': 'active', 'locked': False, 'avatar_url': 'https://secure.gravatar.com/avatar/d426a4bc823547a2902452c9c4906d39bb79fffae818ea89c5bcdddb12bb7ffc?s=80&d=identicon', 'web_url': 'https://gitlab.com/chuanqidota'}, 'assignees': [], 'assignee': None, 'reviewers': [], 'source_project_id': 57091227, 'target_project_id': 57091227, 'labels': [], 'draft': False, 'work_in_progress': False, 'milestone': None, 'merge_when_pipeline_succeeds': False, 'merge_status': 'checking', 'detailed_merge_status': 'preparing', 'sha': '8bc9bfd8f1b2846ec90ce3fff980a19045f1857e', 'merge_commit_sha': None, 'squash_commit_sha': None, 'discussion_locked': None, 'should_remove_source_branch': None, 'force_remove_source_branch': None, 'prepared_at': None, 'reference': '!1', 'references': {'short': '!1', 'relative': '!1', 'full': 'chuanqidota/api-project!1'}, 'web_url': 'https://gitlab.com/chuanqidota/api-project/-/merge_requests/1', 'time_stats': {'time_estimate': 0, 'total_time_spent': 0, 'human_time_estimate': None, 'human_total_time_spent': None}, 'squash': False, 'squash_on_merge': False, 'task_completion_status': {'count': 0, 'completed_count': 0}, 'has_conflicts': False, 'blocking_discussions_resolved': True, 'approvals_before_merge': None, 'subscribed': True, 'changes_count': None, 'latest_build_started_at': None, 'latest_build_finished_at': None, 'first_deployed_to_production_at': None, 'pipeline': None, 'head_pipeline': None, 'diff_refs': None, 'merge_error': None, 'user': {'can_merge': True}}
            获取id,然后再接受合并
        """
        project = self.get_project(project_id)
        if project:
            mr_params = {
                "source_branch": source_branch,
                "target_branch": target_branch,
                "title": title,
                "description": description,
            }
            return project.mergerequests.create(mr_params)
        else:
            return None

    def accept_merge_request(self, project_id, merge_request_id):
        """
            接受merge请求
        :param project_id:
        :param merge_request_id:
        :return:
        """
        project = self.get_project(project_id)
        merge_request = project.mergerequests.get(merge_request_id)
        return merge_request.merge()

    def reject_merge_request(self):
        pass

    def delete_merge_request(self, project_id, merge_request_id):
        """
            删除merge请求
        :param project_id:
        :param merge_request_id:
        :return:
        """
        project = self.get_project(project_id)
        return project.mergerequests.delete(merge_request_id)

    def list_tags(self, project_id):
        """
            列出指定项目的所有标签
        :param project_id: 项目id
        :return: 对象
        """
        project = self.get_project(project_id)
        if project:
            return project.tags.list()
        else:
            return []

    def create_tag(self, project_id, tag_name, ref, message):
        """
            在指定项目中创建新标签
        :param project_id: 项目标签
        :param tag_name: 标签名称
        :param ref: 参考的分支
        :param message: 描述信息
        :return: 对象
        """
        project = self.get_project(project_id)
        if project:
            tag_params = {"tag_name": tag_name, "ref": ref, "message": message}
            return project.tags.create(tag_params)
        else:
            return None

    def delete_tag(self, project_id, tag_name):
        """
            删除tag
        :param project_id:
        :param tag_name:
        :return:
        """
        project = self.get_project(project_id)
        tag = project.tags.get(tag_name)
        tag.delete()

    def upload_file(self, project_id, file_path, content, commit_message, branch="master"):
        """
            上传文件到项目仓库
        :param project_id: 项目id
        :param file_path: 仓库的项目相对路径 ./REDME.md
        :param content: with open("test.txt", "rb") as f: f.read()
        :param commit_message:提交信息
        :param branch:
        :return:
        """
        project = self.get_project(project_id)
        if project:
            try:
                response = project.files.create(
                    {
                        "file_path": file_path,
                        "branch": branch,
                        "content": content.decode(),
                        "commit_message": commit_message,
                    }
                )
                return response
            except gitlab.exceptions.GitlabCreateError as e:
                print(f"Error uploading file: {e}")
                return None
        else:
            return None

    def download_file(self, project_id, file_path, ref="master"):
        """
            从项目仓库下载文件
        :param project_id: 项目id
        :param file_path: 仓库中的文件相对路径
        :param ref: 分支
        :return:
        """
        project = self.get_project(project_id)
        if project:
            try:
                file_content = project.files.raw(file_path, ref=ref)
                return file_content.content
            except gitlab.exceptions.GitlabGetError as e:
                print(f"Error downloading file: {e}")
                return None
        else:
            return None

    def delete_file(self, project_id, file_path, commit_message, branch="master"):
        """
            删除项目仓库中的文件
        :param project_id: 项目id
        :param file_path: 仓库中的文件相对路径
        :param commit_message: 提交信息
        :param branch: 分支
        :return:
        """
        project = self.get_project(project_id)
        if project:
            try:
                project.files.delete(file_path, branch=branch, commit_message=commit_message)
                return True
            except gitlab.exceptions.GitlabDeleteError as e:
                print(f"Error deleting file: {e}")
                return False
        else:
            return False

    def get_file_content(self, project_id, file_path, ref="master"):
        """
            获取项目仓库中指定文件的内容
        :param project_id: 项目id
        :param file_path: 仓库中的文件相对路径
        :param ref: 分支
        :return:
        """
        project = self.get_project(project_id)
        if project:
            try:
                file_data = project.files.get(file_path, ref=ref)
                return file_data.decode()
            except gitlab.exceptions.GitlabGetError as e:
                print(f"Error getting file content: {e}")
                return None
        else:
            return None

    def update_file_content(self, project_id, file_path, content, commit_message, branch="master"):
        pass


if __name__ == '__main__':
    # 使用示例
    YOUR_GITLAB_URL = "https://gitlab.com/"
    YOUR_PRIVATE_TOKEN = "glpat-6Ua4cvm5QizX1Zv1xgc8"

    manager = GitLabManager(YOUR_GITLAB_URL, YOUR_PRIVATE_TOKEN)
    # print(manager.list_projects()[0].id)
    # print(manager.create_project("api-project", "api-description"))
    _project_id = 57091227
    # print(manager.get_project(_project_id))
    # print(manager.list_branches(_project_id))

    # 上传文件
    # _file_path = os.path.join(os.getcwd(), "REDME.md")
    # with open(_file_path, "rb") as f:
    #     _content = f.read()
    # manager.upload_file(_project_id, "./REDME.md", _content, "init")

    # 列出项目分支
    # print(manager.list_branches(_project_id))

    # 创建分支
    # print(manager.create_branch(_project_id, "dev", "master"))

    # 创建合并请求
    # print(manager.create_merge_request(_project_id,"dev","master","title-test","description-test"))

    # 获取merge请求列表
    # print(manager.list_merge_requests(_project_id)[0].iid)
    # print(dir(manager.list_merge_requests(_project_id)[0]))

    # 接受合并请求
    # print(manager.accept_merge_request(_project_id,1,"accept-msg"))

    # 删除合并请求
    # print(manager.delete_merge_request(_project_id,1))

    # 创建tag
    # print(manager.create_tag(_project_id,"tag11","master","tag-desc"))

    # 列举出tag
    # print(manager.list_tags(_project_id))

    # 删除tag
    # print(manager.delete_tag(_project_id,"tag11"))

    # 创建组
    # print(manager.create_group("组1","abc","组描述"))

    # 创建保护分支
    # print(manager.protect_branch(_project_id,"dev"))

    # 删除保护分支
    # print(manager.delete_protected_branch(_project_id,"dev"))

    # 删除分支
    # print(manager.delete_branch(_project_id,"dev"))
