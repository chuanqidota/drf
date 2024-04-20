import gitlab


class GitLabManager:
    def __init__(self, url: str = "YOUR_GITLAB_URL", private_token: str = "YOUR_PRIVATE_TOKEN"):
        self.gitlab = gitlab.Gitlab(url, private_token, ssl_verify=True)

    def get_user_info(self, user_id):
        """
            获取指定ID用户的详细信息
        :param user_id: 用户id
        :return:
        """
        return self.gitlab.users.get(user_id)

    def list_projects(self):
        """
            列出所有可访问的项目
        :return:
        """
        return self.gitlab.projects.list(all=True)

    def create_project(self, name, description, visibility="private"):
        """
            创建新项目
        :param name: 项目名称
        :param description: 描述
        :param visibility: 可见行
        :return:
        """
        return self.gitlab.projects.create({"name": name, "description": description, "visibility": visibility})

    def get_project(self, project_id):
        """
            通过ID获取项目
        :param project_id: 项目id
        :return:
        """
        return self.gitlab.projects.get(project_id)

    def list_branches(self, project_id):
        """
            列出指定项目的所有分支
        :param project_id: 项目id
        :return:
        """
        project = self.get_project(project_id)
        if project:
            return project.branches.list()
        else:
            return []

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

    def list_merge_requests(self, project_id, state="opened"):
        """
            列出指定项目中处于特定状态（默认为打开状态）的合并请求
        :param project_id: 项目id
        :param state:
        :return:
        """
        project = self.get_project(project_id)
        if project:
            return project.mergerequests.list(state=state)
        else:
            return []

    def create_merge_request(self, project_id, source_branch, target_branch, title, description=None):
        """
            在指定项目中创建新的合并请求
        :param project_id: 项目id
        :param source_branch: 源分支
        :param target_branch: 目的分支
        :param title: 标题
        :param description: 描述
        :return:
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

    def list_tags(self, project_id):
        """
            列出指定项目的所有标签
        :param project_id: 项目id
        :return:
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
        :param ref: 参考
        :param message: 消息
        :return:
        """
        project = self.get_project(project_id)
        if project:
            tag_params = {"tag_name": tag_name, "ref": ref, "message": message}
            return project.tags.create(tag_params)
        else:
            return None

    def upload_file(self, project_id, file_path, content, branch="master", commit_message=""):
        """
            上传文件到项目仓库
        :param project_id:
        :param file_path:
        :param content:
        :param branch:
        :param commit_message:
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
        :param project_id:
        :param file_path:
        :param ref:
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

    def delete_file(self, project_id, file_path, branch="master", commit_message=""):
        """
            删除项目仓库中的文件
        :param project_id:
        :param file_path:
        :param branch:
        :param commit_message:
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
        :param project_id:
        :param file_path:
        :param ref:
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

    def create_group(self, name, path, description=None):
        """
            创建新的用户组
        :param name:
        :param path:
        :param description:
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
            列出所有可访问的用户组
        :return:
        """
        return self.gitlab.groups.list(all=True)

    def get_group_details(self, group_id):
        """
            根据组 ID 获取单个组的详细信息
        :param group_id:
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
        group = self.get_group_details(group_id)
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


if __name__ == '__main__':
    # 使用示例
    manager = GitLabManager("YOUR_GITLAB_URL", "YOUR_PRIVATE_TOKEN")
    projects = manager.list_projects()
    print(f"Available projects: {len(projects)}")
