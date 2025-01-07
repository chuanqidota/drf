import gitlab

# https://python-gitlab.readthedocs.io/en/stable/index.html
# gitlab接口文档 https://docs.gitlab.com/ee/api/rest/

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
    # 成员角色的参数access_level
    GuestAccessLevel = 10  # 只读访问，可以查看项目和组
    ReporterAccessLevel = 20  # 可以查看项目和组，提交议题和合并请求
    DeveloperAccessLevel = 30  # 含报告者权限，还可以推送至仓库分支和合并请求
    MaintainerAccessLevel = 40  # 包含开发者权限，还可以管理组和项目，包括添加部署密钥、管理合作者、添加组成员等
    OwnerAccessLevel = 50  # 全部权限，可以管理组和项目，以及转移和删除它们

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
            组操作>创建分组-权限可能会被拒
        :param name: 分组的名称可以和path一致
        :param path: 路径
        :param description: 分组描述
        :return:
        """
        group = self.gitlab.groups.create({
            "name": name,
            "path": path,
            "description": description,
        })
        return group

    def list_groups(self):
        """
            组操作>获取组列表
        :return: [<Group id:86096102 name:test>]
        """
        return self.gitlab.groups.list(all=True)

    def get_group(self, group_id):
        """
            组操作>获取单个组
        :param group_id: 组id
        :return:
        <class 'gitlab.v4.objects.groups.Group'> => {'id': 86096102, 'web_url': 'https://gitlab.com/groups/test804017', 'name': 'test', 'path': 'test804017', 'description': '', 'visibility': 'private', 'share_with_group_lock': False, 'require_two_factor_authentication': False, 'two_factor_grace_period': 48, 'project_creation_level': 'developer', 'auto_devops_enabled': None, 'subgroup_creation_level': 'maintainer', 'emails_disabled': False, 'emails_enabled': True, 'mentions_disabled': None, 'lfs_enabled': True, 'math_rendering_limits_enabled': True, 'lock_math_rendering_limits_enabled': False, 'default_branch': None, 'default_branch_protection': 2, 'default_branch_protection_defaults': {'allowed_to_push': [{'access_level': 40}], 'allow_force_push': False, 'allowed_to_merge': [{'access_level': 40}]}, 'avatar_url': None, 'request_access_enabled': True, 'full_name': 'test', 'full_path': 'test804017', 'created_at': '2024-04-22T09:40:13.292Z', 'parent_id': None, 'organization_id': 1, 'shared_runners_setting': 'enabled', 'ldap_cn': None, 'ldap_access': None, 'wiki_access_level': 'enabled', 'shared_with_groups': [], 'runners_token': 'GR1348941BgEJpSXEtoVXSXikUpsy', 'enabled_git_access_protocol': 'all', 'prevent_sharing_groups_outside_hierarchy': False, 'projects': [], 'shared_projects': [], 'shared_runners_minutes_limit': None, 'extra_shared_runners_minutes_limit': None, 'prevent_forking_outside_group': None, 'membership_lock': False}
        """
        group = self.gitlab.groups.get(group_id)
        return group

    def update_group(self, group_id, name=None, path=None, description=None, visibility="private"):
        """
            组操作>修改已有组的属性
        :param group_id: 组id
        :param name: 名称
        :param path: path
        :param description: 描述
        :param visibility: 可见 private, public
        :return: None
        """
        group = self.get_group(group_id)
        group.name = name or group.name
        group.path = path or group.path
        group.description = description or group.description
        group.visibility = visibility or group.visibility
        group.save()

    def delete_group(self, group_id):
        """
            组操作>删除组
        :param group_id: 组id
        :return:
        """
        group = self.get_group(group_id)
        group.delete()

    def create_group_member(self, group_id, user_id, access_level):
        """
            组操作>创建组成员
        :param group_id: 组id
        :param user_id: 用户id
        :param access_level: 权限级别
            NO_ACCESS: int = 0
            MINIMAL_ACCESS: int = 5
            GUEST: int = 10
            REPORTER: int = 20
            DEVELOPER: int = 30
            MAINTAINER: int = 40
            OWNER: int = 50
            ADMIN: int = 60
        :return:
        """
        group = self.get_group(group_id)
        return group.members.create({"user_id": user_id, "access_level": access_level})

    def list_projects_in_group(self, group_id):
        """
            组操作>列出组内的项目
        :param group_id: 组id
        :return:
        """
        group = self.get_group(group_id)
        projects = group.projects.list(all=True)
        return projects

    def list_group_members(self, group_id):
        """
            组操作>列出组内成员
        :param group_id: 组id
        :return:
        [<GroupMember id:8730526 username:chuanqidota>]
        """
        group = self.get_group(group_id)
        return group.members.list(all=True)

    def update_group_members(self, group_id, user_id, access_level):
        """
            组操作>更新组成员：添加、移除或更新成员的角色权限>权限可能被拒
        :param group_id: 组id
        :param user_id: 用户id
        :param access_level: 权限级别
        :return:
        """
        group = self.get_group(group_id)
        return group.members.update(user_id, {"access_level": access_level})

    def delete_group_member(self, group_id, user_id):
        """
            组操作>删除组成员-权限可能被拒绝
        :param group_id: 组id
        :param user_id: 用户id
        :return:
        """
        group = self.get_group(group_id)
        return group.members.delete(user_id)

    def create_user(self, name, username, email, password):
        """
            用户操作>创建用户-权限可能会被拒绝
        :param name: 名称
        :param username: 用户名
        :param email: 邮箱
        :param password: 密码
        :return:
        """
        data = {
            'name': name,
            'username': username,
            'email': email,
            'password': password,
            'reset_password': False  # Set to True if you want the user to reset password on first login
        }
        user = self.gitlab.users.create(data)
        return user

    def list_users(self):
        """
            用户操作>列出用户
        :return:
        """
        users = self.gitlab.users.list(all=True)
        return users

    def get_user_by_id(self, user_id):
        """
            用户操作>获取用户的详细信息根据id
        :param user_id: 用户id
        :return:
        <class 'gitlab.v4.objects.users.User'> => {'id': 8730526, 'username': 'chuanqidota', 'name': 'chuanqidota', 'state': 'active', 'locked': False, 'avatar_url': 'https://secure.gravatar.com/avatar/d426a4bc823547a2902452c9c4906d39bb79fffae818ea89c5bcdddb12bb7ffc?s=80&d=identicon', 'web_url': 'https://gitlab.com/chuanqidota', 'created_at': '2021-04-22T01:37:59.495Z', 'bio': '', 'location': '', 'public_email': '', 'skype': '', 'linkedin': '', 'twitter': '', 'discord': '', 'website_url': '', 'organization': '', 'job_title': '', 'pronouns': '', 'bot': False, 'work_information': None, 'local_time': '12:48 PM'}
        """
        return self.gitlab.users.get(user_id)

    def get_user_by_username(self, username):
        """
            用户操作>获取用户的详细信息根据username
        :param username: 用户名
        :return:
        <class 'gitlab.v4.objects.users.User'> => {'id': 8730526, 'username': 'chuanqidota', 'name': 'chuanqidota', 'state': 'active', 'locked': False, 'avatar_url': 'https://secure.gravatar.com/avatar/d426a4bc823547a2902452c9c4906d39bb79fffae818ea89c5bcdddb12bb7ffc?s=80&d=identicon', 'web_url': 'https://gitlab.com/chuanqidota', 'created_at': '2021-04-22T01:37:59.495Z', 'bio': '', 'location': '', 'public_email': '', 'skype': '', 'linkedin': '', 'twitter': '', 'discord': '', 'website_url': '', 'organization': '', 'job_title': '', 'pronouns': '', 'bot': False, 'work_information': None, 'local_time': '12:48 PM'}
        """
        users = self.gitlab.users.list(all=True, search=username)
        matching_users = [user for user in users if user.username == username]
        if matching_users:
            return matching_users[0]
        else:
            raise ValueError(f"No user found with username '{username}'")

    def update_user(self, user_id, attributes):
        """
            用户操作>更新用户
        :param user_id: 用户id
        :param attributes: 属性 用户的属性和值
        :return:
        """
        user = self.gitlab.users.get(user_id)
        for attr, value in attributes.items():
            setattr(user, attr, value)
        user.save()

    def delete_user_by_id(self, user_id):
        """
            用户操作>删除用户根据id
        :param user_id: 用户id
        :return:
        """
        user = self.gitlab.users.get(user_id)
        user.delete()

    def delete_user_by_username(self, username):
        """
            用户操作>删除用户根据username
        :param username: 用户名
        :return:
        """
        users = self.gitlab.users.list(all=True, search=username)
        matching_users = [user for user in users if user.username == username]
        if matching_users:
            return matching_users[0].delete()
        else:
            raise ValueError(f"No user found with username '{username}'")

    def create_project(self, name, description, visibility="private", group_id=None):
        """
            项目操作>创建新项目
        :param name: 项目名称
        :param description: 描述
        :param visibility: 可见行 private / public
        :param group_id: 组id,如果有此参数则是在组内常见项目
        :return:
        <class 'gitlab.v4.objects.projects.Project'> => {'id': 57183172, 'description': 'test_project', 'name': 'test_project', 'name_with_namespace': 'test / test_project', 'path': 'test_project', 'path_with_namespace': 'test4693117/test_project', 'created_at': '2024-04-23T12:35:01.916Z', 'default_branch': 'main', 'tag_list': [], 'topics': [], 'ssh_url_to_repo': 'git@gitlab.com:test4693117/test_project.git', 'http_url_to_repo': 'https://gitlab.com/test4693117/test_project.git', 'web_url': 'https://gitlab.com/test4693117/test_project', 'readme_url': None, 'forks_count': 0, 'avatar_url': None, 'star_count': 0, 'last_activity_at': '2024-04-23T12:35:01.841Z', 'namespace': {'id': 86176660, 'name': 'test', 'path': 'test4693117', 'kind': 'group', 'full_path': 'test4693117', 'parent_id': None, 'avatar_url': None, 'web_url': 'https://gitlab.com/groups/test4693117'}, 'container_registry_image_prefix': 'registry.gitlab.com/test4693117/test_project', '_links': {'self': 'https://gitlab.com/api/v4/projects/57183172', 'issues': 'https://gitlab.com/api/v4/projects/57183172/issues', 'merge_requests': 'https://gitlab.com/api/v4/projects/57183172/merge_requests', 'repo_branches': 'https://gitlab.com/api/v4/projects/57183172/repository/branches', 'labels': 'https://gitlab.com/api/v4/projects/57183172/labels', 'events': 'https://gitlab.com/api/v4/projects/57183172/events', 'members': 'https://gitlab.com/api/v4/projects/57183172/members', 'cluster_agents': 'https://gitlab.com/api/v4/projects/57183172/cluster_agents'}, 'packages_enabled': True, 'empty_repo': True, 'archived': False, 'visibility': 'private', 'resolve_outdated_diff_discussions': False, 'container_expiration_policy': {'cadence': '1d', 'enabled': False, 'keep_n': 10, 'older_than': '90d', 'name_regex': '.*', 'name_regex_keep': None, 'next_run_at': '2024-04-24T12:35:01.953Z'}, 'repository_object_format': 'sha1', 'issues_enabled': True, 'merge_requests_enabled': True, 'wiki_enabled': True, 'jobs_enabled': True, 'snippets_enabled': True, 'container_registry_enabled': True, 'service_desk_enabled': True, 'service_desk_address': 'contact-project+test4693117-test-project-57183172-issue-@incoming.gitlab.com', 'can_create_merge_request_in': True, 'issues_access_level': 'enabled', 'repository_access_level': 'enabled', 'merge_requests_access_level': 'enabled', 'forking_access_level': 'enabled', 'wiki_access_level': 'enabled', 'builds_access_level': 'enabled', 'snippets_access_level': 'enabled', 'pages_access_level': 'private', 'analytics_access_level': 'enabled', 'container_registry_access_level': 'enabled', 'security_and_compliance_access_level': 'private', 'releases_access_level': 'enabled', 'environments_access_level': 'enabled', 'feature_flags_access_level': 'enabled', 'infrastructure_access_level': 'enabled', 'monitor_access_level': 'enabled', 'model_experiments_access_level': 'enabled', 'model_registry_access_level': 'enabled', 'emails_disabled': False, 'emails_enabled': True, 'shared_runners_enabled': True, 'lfs_enabled': True, 'creator_id': 8730526, 'import_url': None, 'import_type': None, 'import_status': 'none', 'import_error': None, 'open_issues_count': 0, 'description_html': '<p data-sourcepos="1:1-1:12" dir="auto">test_project</p>', 'updated_at': '2024-04-23T12:35:01.916Z', 'ci_default_git_depth': 20, 'ci_forward_deployment_enabled': True, 'ci_forward_deployment_rollback_allowed': True, 'ci_job_token_scope_enabled': False, 'ci_separated_caches': True, 'ci_allow_fork_pipelines_to_run_in_parent_project': True, 'build_git_strategy': 'fetch', 'keep_latest_artifact': True, 'restrict_user_defined_variables': False, 'runners_token': 'GR1348941oWBi7bJ3i-zLCrYfnZY6', 'runner_token_expiration_interval': None, 'group_runners_enabled': True, 'auto_cancel_pending_pipelines': 'enabled', 'build_timeout': 3600, 'auto_devops_enabled': False, 'auto_devops_deploy_strategy': 'continuous', 'ci_config_path': '', 'public_jobs': True, 'shared_with_groups': [], 'only_allow_merge_if_pipeline_succeeds': False, 'allow_merge_on_skipped_pipeline': None, 'request_access_enabled': True, 'only_allow_merge_if_all_discussions_are_resolved': False, 'remove_source_branch_after_merge': True, 'printing_merge_request_link_enabled': True, 'merge_method': 'merge', 'squash_option': 'default_off', 'enforce_auth_checks_on_uploads': True, 'suggestion_commit_message': None, 'merge_commit_template': None, 'squash_commit_template': None, 'issue_branch_template': None, 'warn_about_potentially_unwanted_characters': True, 'autoclose_referenced_issues': True, 'external_authorization_classification_label': '', 'requirements_enabled': False, 'requirements_access_level': 'enabled', 'security_and_compliance_enabled': True, 'compliance_frameworks': []}
        """
        data = {"name": name, "description": description, "visibility": visibility}
        if group_id:
            data.update({"namespace_id": group_id})
        return self.gitlab.projects.create(data)

    def list_projects(self):
        """
            项目操作>列出所有可访问的项目
        :return:
            [<Project id:57200632 path_with_namespace:chuanqidota/test_project1>, <Project id:57183172 path_with_namespace:test4693117/test_project>, <Project id:57091227 path_with_namespace:chuanqidota/api-project>, <Project id:55973645 path_with_namespace:chuanqidota/test_merge>, <Project id:55842206 path_with_namespace:chuanqidota/test-merger>, <Project id:50854258 path_with_namespace:chuanqidota/demo01>, <Project id:50736341 path_with_namespace:chuanqidota/demo>, <Project id:41395023 path_with_namespace:chuanqidota/rbac>, <Project id:40557636 path_with_namespace:chuanqidota/cmdb>, <Project id:34698422 path_with_namespace:chuanqidota/flask>, <Project id:31954731 path_with_namespace:chuanqidota/panda2>, <Project id:31954526 path_with_namespace:chuanqidota/panda>]

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
            项目操作>获取项目根据id
        :param project_id: 项目id
        :return:
        """
        return self.gitlab.projects.get(project_id)

    def get_project_by_name(self, project_name):
        """
            项目操作>获取项目根据名称
        :param project_name: 项目名称
        :return:
        """
        projects = self.gitlab.projects.list(search=project_name)
        if projects:
            return projects[0]
        return None

    def update_project(self, project_id, attributes):
        """
            项目操作>更新项目
        :param project_id: 用户id
        :param attributes: 属性
        :return:
        """
        project = self.get_project(project_id)
        for attr, value in attributes.items():
            setattr(project, attr, value)
        project.save()

    def delete_project(self, project_id):
        """
            项目操作>删除项目
        :param project_id: 项目id
        :return:
        """
        project = self.get_project(project_id)
        project.delete()

    def create_project_member(self, project_id, user_id, access_level):
        """
            项目操作>创建项目成员
        :param project_id: 项目id
        :param user_id: 用户id
        :param access_level: 权限级别
            NO_ACCESS: int = 0
            MINIMAL_ACCESS: int = 5
            GUEST: int = 10
            REPORTER: int = 20
            DEVELOPER: int = 30
            MAINTAINER: int = 40
            OWNER: int = 50
            ADMIN: int = 60
        :return:
        """
        project = self.get_project(project_id)
        return project.members.create({"user_id": user_id, "access_level": access_level})

    def create_branch(self, project_id, branch_name, ref):
        """
            分支操作>创建新分支
            需要提前有一个分支，也就是需要提前上传文件才行
        :param project_id: 项目id
        :param branch_name: 项目名称
        :param ref: 参考那个分支
        :return:
        <class 'gitlab.v4.objects.branches.ProjectBranch'> => {'name': 'dev', 'commit': {'id': '83bef0e59c25d8b1b20551255ea8ef4844bc17a5', 'short_id': '83bef0e5', 'created_at': '2024-04-23T22:48:53.000+00:00', 'parent_ids': ['e8bcf35ba0816b4322fe916e0260abf9b36d0e38'], 'title': 'add README.md', 'message': 'add README.md', 'author_name': 'chuanqidota', 'author_email': 'chuanqidota@126.com', 'authored_date': '2024-04-23T22:48:53.000+00:00', 'committer_name': 'chuanqidota', 'committer_email': 'chuanqidota@126.com', 'committed_date': '2024-04-23T22:48:53.000+00:00', 'trailers': {}, 'extended_trailers': {}, 'web_url': 'https://gitlab.com/test4693117/test_project/-/commit/83bef0e59c25d8b1b20551255ea8ef4844bc17a5'}, 'merged': False, 'protected': False, 'developers_can_push': False, 'developers_can_merge': False, 'can_push': True, 'default': False, 'web_url': 'https://gitlab.com/test4693117/test_project/-/tree/dev'}
        """
        project = self.get_project(project_id)
        return project.branches.create({"branch": branch_name, "ref": ref})

    def list_branches(self, project_id):
        """
            分支操作>列出项目的所有分支
        :param project_id: 项目id
        :return:
            ['dev', 'main']
        """
        project = self.get_project(project_id)
        return [branch.name for branch in project.branches.list()]

    def delete_branch(self, project_id, branch_name):
        """
            分支操作>删除分支
        :param project_id: 项目id
        :param branch_name: 分支名称
        :return:
        """
        project = self.get_project(project_id)
        project.branches.delete(branch_name)

    def create_protect_branch(self, project_id, branch_name,
                              push_access_levels=None,
                              merge_access_levels=None,
                              unprotect_access_levels=None, code_owner_approval_required=False,
                              approvals_required=None, approval_rules=None):
        """
            分支操作>为项目中的分支设置保护规则
        :param project_id:
        :param branch_name:
        :param push_access_levels:
            类型：列表，元素为字典，表示访问级别对象
            含义：定义哪些用户或组可以在受保护分支上推送代码。每个访问级别对象通常包含access_level（整数，表示权限级别）、user_id（用户ID，可选）或group_id（组ID，可选）。
            如何传参：提供一个包含访问级别对象的列表
            push_access_levels = [
                {"access_level": 40, "user_id": 1},
                {"access_level": 30, "group_id": 7}
            ]
        :param merge_access_levels:
            类型：列表，元素为字典，表示访问级别对象
            含义：定义哪些用户或组可以在受保护分支上合并代码。结构同push_access_levels。
            如何传参：类似push_access_levels，提供一个包含访问级别对象的列表
            merge_access_levels=[
                {"access_level": 40, "user_id": 8},
                {"access_level": 30, "group_id": 9}
            ]
        :param unprotect_access_levels:
            类型：列表，元素为字典，表示访问级别对象
            含义：定义哪些用户或组可以解除对受保护分支的保护。结构同push_access_levels。
            如何传参：类似push_access_levels，提供一个包含访问级别对象的列表
            [{"access_level": 50}]
        :param code_owner_approval_required:
            类型：布尔值
            含义：是否要求代码所有者批准才能合并到受保护分支。
            如何传参：传入True表示需要代码所有者批准，传入False表示不需要。例如：code_owner_approval_required = True
        :param approvals_required:
            类型：整数
            含义：合并请求需要获得的最小批准数量。
            如何传参：提供一个整数值，表示所需的批准数量。例如：approvals_required = 2
        :param approval_rules:
            类型：列表，元素为字典，表示审批规则对象
            含义：自定义审批规则，可以指定特定的用户、组或角色需要对合并请求进行审批。
            如何传参：提供一个包含审批规则对象的列表，例如：
            approval_rules = [
                {
                    "name": "Backend Team Approval",
                    "user_ids": [1, 2],
                    "group_ids": [5],
                    "approvals_required": 1
                }
            ]
        :return:
        <class 'gitlab.v4.objects.branches.ProjectProtectedBranch'> => {'id': 100963842, 'name': 'dev', 'push_access_levels': [{'id': 119242780, 'access_level': 40, 'access_level_description': 'Maintainers', 'deploy_key_id': None, 'user_id': None, 'group_id': None}], 'merge_access_levels': [{'id': 106987999, 'access_level': 40, 'access_level_description': 'Maintainers', 'user_id': None, 'group_id': None}], 'allow_force_push': False, 'unprotect_access_levels': [{'id': 51365854, 'access_level': 40, 'access_level_description': 'Maintainers', 'user_id': None, 'group_id': None}], 'code_owner_approval_required': False, 'inherited': False}
        """
        project = self.get_project(project_id)

        return project.protectedbranches.create({
            "name": branch_name,
            "push_access_levels": push_access_levels or [],
            "merge_access_levels": merge_access_levels or [],
            "unprotect_access_levels": unprotect_access_levels or [],
            "code_owner_approval_required": code_owner_approval_required,
            "approvals_required": approvals_required,
            "approval_rules": approval_rules or [],
        })

    def get_protected_branch(self, project_id, branch_name):
        """
            分支操作>获取指定分支的保护规则
        :param project_id:
        :param branch_name:
        :return:
        <class 'gitlab.v4.objects.branches.ProjectProtectedBranch'> => {'id': 100963842, 'name': 'dev', 'push_access_levels': [{'id': 119242780, 'access_level': 40, 'access_level_description': 'Maintainers', 'deploy_key_id': None, 'user_id': None, 'group_id': None}], 'merge_access_levels': [{'id': 106987999, 'access_level': 40, 'access_level_description': 'Maintainers', 'user_id': None, 'group_id': None}], 'allow_force_push': False, 'unprotect_access_levels': [{'id': 51365854, 'access_level': 40, 'access_level_description': 'Maintainers', 'user_id': None, 'group_id': None}], 'code_owner_approval_required': False, 'inherited': False}
        """
        project = self.get_project(project_id)
        return project.protectedbranches.get(branch_name)

    def update_protected_branch(self, project_id, branch_name, push_access_levels=None,
                                merge_access_levels=None,
                                unprotect_access_levels=None,
                                code_owner_approval_required=None,
                                approvals_required=None,
                                approval_rules=None):
        """
            分支操作>修改已有分支的保护规则
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

        return protected_branch.update({
            "push_access_levels": push_access_levels or protected_branch.push_access_levels,
            "merge_access_levels": merge_access_levels or protected_branch.merge_access_levels,
            "unprotect_access_levels": unprotect_access_levels or protected_branch.unprotect_access_levels,
            "code_owner_approval_required": code_owner_approval_required or protected_branch.code_owner_approval_required,
            "approvals_required": approvals_required or protected_branch.approvals_required,
            "approval_rules": approval_rules or protected_branch.approval_rules,
        })

    def delete_protected_branch(self, project_id, branch_name):
        """
            分支操作>把保护分支删除-分支直接删除
        :param project_id: 项目id
        :param branch_name: 分支名称
        :return:
        """
        project = self.get_project(project_id)
        protected_branch = project.protectedbranches.get(branch_name)
        protected_branch.delete()

    def set_default_branch(self, project_id, branch_name):
        """
            分支操作>设置默认分支
        :param project_id: 项目id
        :param branch_name: 默认分支
        :return:
        """
        project = self.get_project(project_id)
        project.default_branch = branch_name
        project.save()

    def create_merge_request(self, project_id, source_branch, target_branch, title, description=None):
        """
            合并请求操作>在指定项目中创建新的合并请求,这里存在失败的可能,需要特殊处理
        :param project_id: 项目id
        :param source_branch: 源分支
        :param target_branch: 目的分支
        :param title: 标题
        :param description: 描述
        :return:
            对象可以通过点出来
            {'id': 297344392, 'iid': 1, 'project_id': 57091227, 'title': 'title-test', 'description': 'description-test', 'state': 'opened', 'created_at': '2024-04-22T03:19:17.365Z', 'updated_at': '2024-04-22T03:19:17.365Z', 'merged_by': None, 'merge_user': None, 'merged_at': None, 'closed_by': None, 'closed_at': None, 'target_branch': 'master', 'source_branch': 'dev', 'user_notes_count': 0, 'upvotes': 0, 'downvotes': 0, 'author': {'id': 8730526, 'username': 'chuanqidota', 'name': 'chuanqidota', 'state': 'active', 'locked': False, 'avatar_url': 'https://secure.gravatar.com/avatar/d426a4bc823547a2902452c9c4906d39bb79fffae818ea89c5bcdddb12bb7ffc?s=80&d=identicon', 'web_url': 'https://gitlab.com/chuanqidota'}, 'assignees': [], 'assignee': None, 'reviewers': [], 'source_project_id': 57091227, 'target_project_id': 57091227, 'labels': [], 'draft': False, 'work_in_progress': False, 'milestone': None, 'merge_when_pipeline_succeeds': False, 'merge_status': 'checking', 'detailed_merge_status': 'preparing', 'sha': '8bc9bfd8f1b2846ec90ce3fff980a19045f1857e', 'merge_commit_sha': None, 'squash_commit_sha': None, 'discussion_locked': None, 'should_remove_source_branch': None, 'force_remove_source_branch': None, 'prepared_at': None, 'reference': '!1', 'references': {'short': '!1', 'relative': '!1', 'full': 'chuanqidota/api-project!1'}, 'web_url': 'https://gitlab.com/chuanqidota/api-project/-/merge_requests/1', 'time_stats': {'time_estimate': 0, 'total_time_spent': 0, 'human_time_estimate': None, 'human_total_time_spent': None}, 'squash': False, 'squash_on_merge': False, 'task_completion_status': {'count': 0, 'completed_count': 0}, 'has_conflicts': False, 'blocking_discussions_resolved': True, 'approvals_before_merge': None, 'subscribed': True, 'changes_count': None, 'latest_build_started_at': None, 'latest_build_finished_at': None, 'first_deployed_to_production_at': None, 'pipeline': None, 'head_pipeline': None, 'diff_refs': None, 'merge_error': None, 'user': {'can_merge': True}}
            获取iid,然后再接受合并
        """
        project = self.get_project(project_id)
        data = {
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description,
        }
        return project.mergerequests.create(data)

    def list_merge_requests(self, project_id, state="opened"):
        """
            合并请求操作>列出指定项目中处于特定状态（默认为打开状态）的合并请求
        :param project_id: 项目id
        :param state:
        :return:
            [<ProjectMergeRequest iid:1>]
            返回的是对象 iid是项目merge的id
        """
        project = self.get_project(project_id)
        return project.mergerequests.list(state=state)

    def accept_merge_request(self, project_id, merge_request_iid):
        """
            合并请求操作>接受merge请求
        :param project_id: 项目id
        :param merge_request_iid: 合并请求iid
        :return:
        """
        project = self.get_project(project_id)
        merge_request = project.mergerequests.get(merge_request_iid)
        return merge_request.merge()

    def reject_merge_request(self, project_id, merge_request_iid):
        """
            合并请求操作>拒绝合并请求
        :param project_id: 项目id
        :param merge_request_iid: 合并请求iid
        :return:
        """
        project = self.get_project(project_id)
        merge_request = project.mergerequests.get(merge_request_iid)
        merge_request.state_event = 'close'
        merge_request.save()

    def delete_merge_request(self, project_id, merge_request_iid):
        """
            合并请求操作>删除merge请求
        :param project_id: 项目id
        :param merge_request_iid: 合并请求iid
        :return:
        """
        project = self.get_project(project_id)
        return project.mergerequests.delete(merge_request_iid)

    def create_tag(self, project_id, tag_name, ref, message):
        """
            标签操作>在指定项目中创建新标签
        :param project_id: 项目标签
        :param tag_name: 标签名称
        :param ref: 参考的分支
        :param message: 描述信息
        :return:
        <class 'gitlab.v4.objects.tags.ProjectTag'> => {'name': 'v1.0.0', 'message': 'test_tag', 'target': '40f4a6501e07e70a5fdb13f3784f9ef189843267', 'commit': {'id': '596d0b95b7fb21ed5e84c1d08740edfe8180b135', 'short_id': '596d0b95', 'created_at': '2024-04-23T23:11:41.000+00:00', 'parent_ids': ['83bef0e59c25d8b1b20551255ea8ef4844bc17a5'], 'title': 'add README.md', 'message': 'add README.md', 'author_name': 'chuanqidota', 'author_email': 'chuanqidota@126.com', 'authored_date': '2024-04-23T23:11:41.000+00:00', 'committer_name': 'chuanqidota', 'committer_email': 'chuanqidota@126.com', 'committed_date': '2024-04-23T23:11:41.000+00:00', 'trailers': {}, 'extended_trailers': {}, 'web_url': 'https://gitlab.com/test4693117/test_project/-/commit/596d0b95b7fb21ed5e84c1d08740edfe8180b135'}, 'protected': False, 'created_at': None}
        """
        project = self.get_project(project_id)
        tag_params = {"tag_name": tag_name, "ref": ref, "message": message}
        return project.tags.create(tag_params)

    def list_tags(self, project_id):
        """
            标签操作>列出指定项目的所有标签
        :param project_id: 项目id
        :return:
            [<ProjectTag name:v1.0.0>]
        """
        project = self.get_project(project_id)
        return project.tags.list()

    def delete_tag(self, project_id, tag_name):
        """
            标签操作>删除tag
        :param project_id: 项目id
        :param tag_name: 标签名称
        :return:
        """
        project = self.get_project(project_id)
        tag = project.tags.get(tag_name)
        tag.delete()

    def upload_file(self, project_id, file_path, content, commit_message, branch="master"):
        """
            文件操作>上传文件到项目仓库
            初次提交的时候指定分支就会在改分支上提交文件
            后续需要新拉分支
        :param project_id: 项目id
        :param file_path: 仓库的项目相对路径 REDME.md
        :param content: with open("test.txt", "rb") as f: f.read()
        :param commit_message:提交信息
        :param branch:
        :return:
        """
        project = self.get_project(project_id)
        response = project.files.create(
            {
                "file_path": file_path,
                "branch": branch,
                "content": content.decode(),
                "commit_message": commit_message,
            }
        )
        return response

    def get_file_content(self, project_id, file_path, ref="master"):
        """
            文件操作>获取项目仓库中指定文件的内容
        :param project_id: 项目id
        :param file_path: 仓库中的文件相对路径
        :param ref: 分支
        :return:byte 这个时候应该可以写入文件中
        """
        project = self.get_project(project_id)
        file_content = project.files.get(file_path, ref=ref)
        return file_content

    def delete_file(self, project_id, file_path, commit_message, branch="master"):
        """
            文件操作>删除项目仓库中的文件
        :param project_id: 项目id
        :param file_path: 仓库中的文件相对路径
        :param commit_message: 提交信息
        :param branch: 分支
        :return:
        """
        project = self.get_project(project_id)
        return project.files.delete(file_path, branch=branch, commit_message=commit_message)

    def update_file_content(self, project_id, file_path, new_content, commit_message, branch="master"):
        """
            文件操作>更新文件内容
        :param project_id: 项目id
        :param file_path: 文件路径
        :param new_content: 新内容
        :param commit_message: 提交信息
        :param branch: 分支
        :return:
        """
        project = self.get_project(project_id)
        file = project.files.get(file_path=file_path, ref=branch)
        file.content = new_content
        file.save(branch=branch, commit_message=commit_message)

    def list_webhook(self, project_id):
        """
            Webhook操作>列出指定项目的所有Webhook
        :param project_id: 项目id
        :return:
        """
        project = self.get_project(project_id)
        return project.hooks.list()

    def create_webhook(self, project_id, url, token, push_events=True, tag_push_events=True, merge_requests_events=True,
                       enable_ssl_verification=True):
        """
            Webhook操作>创建新Webhook
        :param project_id: 项目id
        :param url: Webhook的URL
        :param token: Webhook的Secret Token
        :param push_events: 是否接收推送事件
        :param tag_push_events: 是否接收标签推送事件
        :param merge_requests_events: 是否接收合并请求事件
        :param enable_ssl_verification: 是否启用SSL验证
        :return:
        """
        project = self.get_project(project_id)
        return project.hooks.create(
            {
                "url": url,
                "token": token,
                "push_events": push_events,
                "tag_push_events": tag_push_events,
                "merge_requests_events": merge_requests_events,
                "enable_ssl_verification": enable_ssl_verification,
            }
        )

    def delete_webhook(self, project_id, webhook_id):
        """
            Webhook操作>删除Webhook
        :param project_id: 项目id
        :param webhook_id: Webhook的id
        :return:
        """
        project = self.get_project(project_id)
        return project.hooks.delete(webhook_id)

    def get_webhook(self, project_id, webhook_id):
        """
            Webhook操作>获取单个Webhook
        :param project_id: 项目id
        :param webhook_id: Webhook的id
        :return:
        """
        project = self.get_project(project_id)
        return project.hooks.get(webhook_id)

    def update_webhook(self, project_id, webhook_id, url, token, push_events=True, tag_push_events=True,
                       merge_requests_events=True):
        """
            Webhook操作>更新Webhook
        :param project_id: 项目id
        :param webhook_id: Webhook的id
        :param url: Webhook的URL
        :param token: Webhook的Secret Token
        :param push_events: 是否接收推送事件
        :param tag_push_events: 是否接收标签推送事件
        :param merge_requests_events: 是否接收合并请求事件
        :return:
        """
        project = self.get_project(project_id)
        webhook = project.hooks.get(webhook_id)
        webhook.url = url
        webhook.token = token
        webhook.push_events = push_events
        webhook.tag_push_events = tag_push_events
        webhook.merge_requests_events = merge_requests_events
        webhook.save()
        return


if __name__ == '__main__':
    # 使用示例
    YOUR_GITLAB_URL = "https://gitlab.com/"
    YOUR_PRIVATE_TOKEN = "glpat-6Ua4cvm5QizX1Zv1xgc8"

    manager = GitLabManager(YOUR_GITLAB_URL, YOUR_PRIVATE_TOKEN)

    # 组操作>创建分组
    # group = manager.create_group("test_group", "test_group","group-desc")
    # print(group)

    # 组操作>获取组列表
    # groups = manager.list_groups()
    # print(groups)

    # 组操作>获取单个组
    # group = manager.get_group(86096102)
    # print(group)

    # 组操作>修改已有组的属性
    # updated_group = manager.update_group(86096102, "test2", "test8040171111111", "desc-fix")
    # print(updated_group)

    # 组操作>删除组
    # manager.delete_group(86096102)

    # 组操作>列出组内的项目
    # projects = manager.list_projects_in_group(86176660)
    # print(projects)

    # 项目操作>创建新项目
    # project = manager.create_project("test_project", "test_project", "private",86176660)
    # print(project)

    # 用户操作>创建用户
    # user = manager.create_user("测试", "test_user", "test_user@qq.com", "test_user")
    # print(user)

    # 组操作>创建组成员
    # member = manager.create_group_member(86176660, 1, 50)
    # print(member)

    # 组操作>列出组内成员
    # members = manager.list_group_members(86176660)
    # print(members)

    # 组操作>更新组成员：添加、移除或更新成员的角色权限
    # member = manager.update_group_members(86176660, 8730526, manager.OwnerAccessLevel)
    # print(member)

    # 组操作>删除组成员
    # print(manager.delete_group_member(86176660, 8730526))

    #  用户操作>列出用户
    # users = manager.list_users()
    # print(users)

    # 用户操作>获取用户的详细信息根据id
    # user = manager.get_user_by_id(8730526)
    # print(user)

    # 用户操作>获取用户的详细信息根据username
    # user = manager.get_user_by_username("chuanqidota")
    # print(user)

    # 项目操作>创建新项目
    # project = manager.create_project("test_project", "test_project", "private")
    # print(project)

    # 项目操作>列出所有可访问的项目
    # projects = manager.gitlab.projects.list(owned=True)
    # print(projects)

    # 项目操作>获取项目根据名称
    # project = manager.get_project_by_name("test_project")
    # print(project)

    #  项目操作>更新项目
    # attributes = {
    #     "name": "test_project222",
    #     "description": "22222",
    #     "visibility": "public"
    # }
    # project = manager.update_project(project_id=57200632, attributes=attributes)
    # print(project)

    # 项目操作>删除项目
    # print(manager.delete_project(57200632))

    # 57183172
    # 分支操作>创建新分支
    # print(manager.create_branch(57183172, "dev", "master"))

    # 文件操作>上传文件到项目仓库
    # with open("REDME.md", "rb") as f:
    #     contenct = f.read()
    #     print(manager.upload_file(57183172, "./README3.md", contenct, "add README.md", "dev"))

    # 分支操作>创建新分支
    # print(manager.create_branch(57183172, "dev", "main"))

    # 分支操作>列出项目的所有分支
    # print(manager.list_branches(57183172))

    # 分支操作>删除分支
    # print(manager.delete_branch(57183172, "dev"))

    # 分支操作>为项目中的分支设置保护规则
    # print(manager.create_protect_branch(57183172, "dev"))

    # 分支操作>获取指定分支的保护规则
    #  print(manager.get_protected_branch(57183172, "dev"))

    # 分支操作>把保护分支删除
    # print(manager.delete_protected_branch(57183172, "dev"))

    # 分支操作>设置默认分支
    # print(manager.set_default_branch(57183172, "dev"))

    # 合并请求操作
    # print(manager.create_merge_request(57183172, "dev", "main", "test_merge_request", "test_merge_request_desc"))

    # 合并请求操作
    # print(manager.list_merge_requests(57183172))

    # 合并请求操作>拒绝合并请求
    # print(manager.reject_merge_request(57183172, 1))

    # 合并请求操作>删除merge请求
    # print(manager.delete_merge_request(57183172, 1))

    # 标签操作>在指定项目中创建新标签
    # print(manager.create_tag(57183172, "v1.0.0", "dev", "test_tag"))

    # 标签操作>列出指定项目的所有标签
    # print(manager.list_tags(57183172))

    # 标签操作>删除标签
    # print(manager.delete_tag(57183172, "v1.0.0"))

    # 文件操作>从项目仓库下载文件
    # print(manager.download_file(57183172, "README.md", "main"))

    # 文件操作>删除项目仓库中的文件
    # print(manager.delete_file(57183172, "README.md", "delete_file", "main"))

    # 文件操作>更新项目仓库中的文件
    # with open("./REDME.md", "rb") as f:
    #     content = f.read()
    #     print(manager.update_file_content(57183172, "README1.md", content, "update-file","main"))
