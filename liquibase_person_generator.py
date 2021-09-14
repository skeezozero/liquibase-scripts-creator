import os
import sys
import yaml

SCRIPT_VERSION = '1.1.0'
ROLE_NAME_CONSTANT = '$ROLE_NAME'
CHANGE_SET_NAME_CONSTANT = '$change_set_name'
AUTHOR_CONSTANT = '$author'
COMMENT_CONSTANT = '$comment'
CHANGE_SET_CONSTANT = '$change_set'
CONTEXT_CONSTANT = '$context'
NAME_CONSTANT = '$NAME'
USERNAME_CONSTANT = '$USERNAME'
AUTHORITY_NAME_CONSTANT = '$AUTHORITY_NAME'
MODE_ROLE = 1
MODE_AUTHORITY = 2
MODE_USER = 3
MODE_AUTHORITIES_TO_ROLES = 4
MODE_USERS_TO_ROLES = 5

START_INFO = f'''
Liquibase Script Generator v <version>
'''.replace('<version>', SCRIPT_VERSION)
HELP_INFO = '''Options:
1. Specify yml absolute path with parameters. Example: "python3 liquibase_person_generator.py C://script/example.yml"
2. Create example .yml file: "python3 liquibase_person_generator.py createExample"'''
CUMULATIVE_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
        xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog ../dbchangelog-3.5.xsd">

$file_template

</databaseChangeLog>
'''
CUMULATIVE_FILE_TEMPLATE = '    <include file="$file_name" relativeToChangelogFile="true"/>'
CHANGE_SET_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
        xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog ../dbchangelog-3.5.xsd"
        context="$context">

$change_set

</databaseChangeLog>'''
CHANGE_SET_SQL_TEMPLATE = '''    <changeSet id="$change_set_name" author="$author" logicalFilePath="path-independent">
        <comment>$comment</comment>
        <sql>
$sql
        </sql>
    </changeSet>'''
SQL_ROLE_CREATION_TEMPLATE = '''            insert into ROLE(NAME, DESCRIPTION) values ('$NAME', '$DESCRIPTION');'''
SQL_ROLE_AUDIT_TEMPLATE = '''            insert into ROLE_AUDIT(REVISION_ID, REVISION_TYPE, NAME, DESCRIPTION, ID)
            select (select max(REVISION_ID) from REVISION_INFO), 0, NAME, DESCRIPTION, ID
            from ROLE
            where NAME = '$NAME';'''
SQL_AUTHORITY_CREATION_TEMPLATE = '''            insert into AUTHORITY(NAME, DESCRIPTION) values ('$NAME', '$DESCRIPTION');'''
SQL_AUTHORITY_AUDIT_TEMPLATE = '''            insert into AUTHORITY_AUDIT(REVISION_ID, REVISION_TYPE, NAME, DESCRIPTION, ID)
            select (select max(REVISION_ID) from REVISION_INFO), 0, NAME, DESCRIPTION, ID
            from AUTHORITY
            where NAME = '$NAME';'''
SQL_AUTHORITY_TO_ROLE_CREATION_TEMPLATE = '''            insert into ROLES_AUTHORITIES(AUTHORITY_ID, ROLE_ID) 
            values ((select ID from AUTHORITY where NAME = '$AUTHORITY_NAME'), (select ID from ROLE where NAME = '$ROLE_NAME'));'''
SQL_AUTHORITY_TO_ROLE_AUDIT_TEMPLATE = '''            insert into ROLES_AUTHORITIES_AUDIT(REVISION_ID, REVISION_TYPE, ROLE_ID, AUTHORITY_ID)
            select (select max(REVISION_ID) from REVISION_INFO), 0, (select ID from ROLE where NAME = '$ROLE_NAME'), ID
            from AUTHORITY
            where NAME = '$AUTHORITY_NAME';'''
SQL_USER_CREATION_TEMPLATE = '''            insert into USER_DETAILS (ACCOUNT_NON_EXPIRED, ACCOUNT_NON_LOCKED, CREDENTIALS_NON_EXPIRED, ENABLED, FIRST_NAME, LAST_NAME, MIDDLE_NAME, PASSWORD, USERNAME, DOMAIN, EMAIL)
            values ($ACCOUNT_NON_EXPIRED, $ACCOUNT_NON_LOCKED, $CREDENTIALS_NON_EXPIRED, $ENABLED, '$FIRST_NAME', '$LAST_NAME', '$MIDDLE_NAME', '$PASSWORD', '$USERNAME', '$DOMAIN', $EMAIL);'''
SQL_USER_TO_ROLE_TEMPLATE = '''            insert into USER_DETAILS_ROLES(ROLE_ID, USER_DETAILS_ID) 
            values ((select ID from ROLE where NAME = '$ROLE_NAME'), (select ID from USER_DETAILS where USERNAME = '$USERNAME'));'''
SQL_USER_AUDIT_TEMPLATE = '''            insert into USER_DETAILS_AUDIT(REVISION_ID, REVISION_TYPE, ID, ACCOUNT_NON_EXPIRED, ACCOUNT_NON_LOCKED, CREDENTIALS_NON_EXPIRED, DOMAIN, EMAIL, ENABLED, FIRST_NAME, LAST_NAME, MIDDLE_NAME, PASSWORD, USERNAME, PASSWORD_CHANGE_DATE)
            select (select max(REVISION_ID) from REVISION_INFO), 0, ID, ACCOUNT_NON_EXPIRED, ACCOUNT_NON_LOCKED, CREDENTIALS_NON_EXPIRED, DOMAIN, EMAIL, ENABLED, FIRST_NAME, LAST_NAME, MIDDLE_NAME, PASSWORD, USERNAME, PASSWORD_CHANGE_DATE
            from USER_DETAILS
            where USERNAME = '$USERNAME';'''
SQL_USER_TO_ROLE_AUDIT_TEMPLATE = '''            insert into USER_DETAILS_ROLES_AUDIT(REVISION_ID, REVISION_TYPE, ROLE_ID, USER_DETAILS_ID)
            select (select max(REVISION_ID) from REVISION_INFO), 0, (select ID from ROLE where NAME = '$ROLE_NAME'), ID
            from USER_DETAILS
            where USERNAME = '$USERNAME';'''
SQL_NEW_REVISION_RECORD = '            call NEW_REVISION_RECORD();'
EXAMPLE_YML = '''version: 5.6.0
date: 2021-07-23
author: Test Testovich

new-roles:
  context:
    - production
    - test
  roles:
    - name: TEST
      description: test_role_description

new-authorities:
  context: test
  authorities:
    - name: test_authority_1
      description: test_authority_1_description
      roles: null
    - name: test_authority_2
      description: test_authority_2_description
      roles:
        - DEVELOPER
        - TEST

new-users:
  context:
    - production
    - test
  users:
    - accountNonExpired: true
      accountNonLocked: true
      credentialsNonExpired: true
      enabled: true
      firstName: Иван
      lastName: Иванов
      middleName: Иванович
      password: qwerty
      username: ivan_ivanov
      domain: MOSCOW.NET
      email: null
      roles:
        - DEVELOPER
        - TEST
    - accountNonExpired: true
      accountNonLocked: true
      credentialsNonExpired: true
      enabled: true
      firstName: Петр
      lastName: Петров
      middleName: Петрович
      password: qwerty
      username: petr_petrov
      domain: MOSCOW.NET
      email: petrov@local.host
      roles: null

authorities-to-roles:
  context:
    - test
  link:
    - authorities:
        - existing_authority1
        - existing_authority2
      to-roles:
        - DEVELOPER
    - authorities:
        - existing_authority3
      to-roles:
        - TEST
        - DEVELOPER

users-to-roles:
  context:
    - production
    - test
  link:
    - usernames:
        - test_user1
        - test_user2
      to-roles:
        - DEVELOPER
    - usernames:
        - test_user3
      to-roles:
        - TEST
        - DEVELOPER'''


class Properties:

    def __init__(self, yml_properties: dict):
        self.version = yml_properties['version']
        self.date = str(yml_properties['date']).replace('-', '')
        self.author = yml_properties['author']

        self.roles = []
        self.authorities = []
        self.users = []
        self.authorities_to_roles = []
        self.users_to_roles = []

        self.roles_context = self.__set_context(yml_properties, 'new-roles')
        self.users_context = self.__set_context(yml_properties, 'new-users')
        self.authorities_context = self.__set_context(yml_properties, 'new-authorities')
        self.authorities_to_roles_context = self.__set_context(yml_properties, 'authorities-to-roles')
        self.users_to_roles_context = self.__set_context(yml_properties, 'users-to-roles')

        if self.users_context is not None:
            for user in yml_properties['new-users']['users']:
                self.users.append(User(user))
        if self.roles_context is not None:
            for role in yml_properties['new-roles']['roles']:
                self.roles.append(Role(role))
        if self.authorities_context is not None:
            for authority in yml_properties['new-authorities']['authorities']:
                self.authorities.append(Authority(authority))
        if self.authorities_to_roles_context is not None:
            for authorities_roles in yml_properties['authorities-to-roles']['link']:
                self.authorities_to_roles.append(AuthoritiesToRoles(authorities_roles))
        if self.users_to_roles_context is not None:
            for users_roles in yml_properties['users-to-roles']['link']:
                self.users_to_roles.append(UsersToRoles(users_roles))

    def has_new_roles(self) -> bool:
        return self.roles is not None and self.roles_context is not None

    def has_new_authorities(self) -> bool:
        return self.authorities is not None and self.authorities_context is not None

    def has_new_users(self) -> bool:
        return self.users is not None and self.users_context is not None

    def has_new_authorities_to_roles(self) -> bool:
        return self.authorities_to_roles is not None and self.authorities_to_roles_context is not None

    def has_new_users_to_roles(self) -> bool:
        return self.users_to_roles is not None and self.users_to_roles_context is not None

    def has_new_data_in_properties(self) -> bool:
        return self.has_new_users() or self.has_new_roles() or self.has_new_authorities() or \
               self.has_new_authorities_to_roles() or self.has_new_users_to_roles()

    def __set_context(self, yml_properties: dict, first_level_filed_name: str):
        try:
            return ' OR '.join(list(yml_properties[first_level_filed_name]['context']))
        except KeyError:
            return None


class User:

    def __init__(self, person: dict):
        self.account_non_expired = person['accountNonExpired']
        self.account_non_locked = person['accountNonLocked']
        self.credentials_non_expired = person['credentialsNonExpired']
        self.enabled = person['enabled']
        self.first_name = person['firstName']
        self.last_name = person['lastName']
        self.middle_name = person['middleName']
        self.password = person['password']
        self.username = person['username']
        self.domain = person['domain']
        self.email = person['email']
        try:
            self.roles = person['roles']
        except KeyError:
            self.roles = None


class Authority:

    def __init__(self, authority: dict):
        self.name = authority['name']
        self.description = authority['description']
        try:
            self.roles = authority['roles']
        except KeyError:
            self.roles = None


class Role:

    def __init__(self, role: dict):
        self.name = role['name']
        self.description = role['description']


class AuthoritiesToRoles:

    def __init__(self, auth_to_roles: dict):
        self.authorities = auth_to_roles['authorities']
        self.to_roles = auth_to_roles['to-roles']


class UsersToRoles:

    def __init__(self, users_to_roles: dict):
        self.users = users_to_roles['usernames']
        self.to_roles = users_to_roles['to-roles']


def check_args_and_get_yml_path() -> str:
    args = sys.argv
    if len(args) != 2:
        print('Arguments Error\n')
        print(HELP_INFO)
        exit(1)
    if 'createExample' in args[1]:
        example_file_path = f'{os.getcwd()}/example_yml_file.yml'
        example_file = open(example_file_path, "w")
        example_file.write(EXAMPLE_YML)
        example_file.close()
        print(f'Create example .yml file in {example_file_path}')
        exit(0)
    return str(args[1])


def create_dir(properties: Properties) -> str:
    dir_path = f'{os.getcwd()}/v-{properties.version}'
    os.mkdir(dir_path)
    return dir_path


def create_cumulative_file(liquibase_dir_path: str, properties: Properties) -> list:
    cumulative_file_path = f'{liquibase_dir_path}/changelog-v-{properties.version}_cumulative.xml'
    cumulative_file = open(cumulative_file_path, "w")
    file_name_constant = '$file_name'

    changelog_file_names_list = []
    changelog_counter = 1
    changelog_file_text = ''

    if properties.has_new_roles():
        file_name = f'{properties.date}_00{str(changelog_counter)}_DML_roles.xml'
        changelog_file_text += CUMULATIVE_FILE_TEMPLATE.replace(file_name_constant, file_name)
        changelog_counter += 1
        changelog_file_names_list.append(file_name)

    if properties.has_new_authorities():
        if len(changelog_file_text) != 0:
            changelog_file_text += '\n'
        file_name = f'{properties.date}_00{str(changelog_counter)}_DML_authorities.xml'
        changelog_file_text += CUMULATIVE_FILE_TEMPLATE.replace(file_name_constant, file_name)
        changelog_counter += 1
        changelog_file_names_list.append(file_name)

    if properties.has_new_users():
        if len(changelog_file_text) != 0:
            changelog_file_text += '\n'
        file_name = f'{properties.date}_00{str(changelog_counter)}_DML_users.xml'
        changelog_file_text += CUMULATIVE_FILE_TEMPLATE.replace(file_name_constant, file_name)
        changelog_counter += 1
        changelog_file_names_list.append(file_name)

    if properties.has_new_authorities_to_roles():
        if len(changelog_file_text) != 0:
            changelog_file_text += '\n'
        file_name = f'{properties.date}_00{str(changelog_counter)}_DML_authorities_to_roles.xml'
        changelog_file_text += CUMULATIVE_FILE_TEMPLATE.replace(file_name_constant, file_name)
        changelog_counter += 1
        changelog_file_names_list.append(file_name)

    if properties.has_new_users_to_roles():
        if len(changelog_file_text) != 0:
            changelog_file_text += '\n'
        file_name = f'{properties.date}_00{str(changelog_counter)}_DML_users_to_roles.xml'
        changelog_file_text += CUMULATIVE_FILE_TEMPLATE.replace(file_name_constant, file_name)
        changelog_counter += 1
        changelog_file_names_list.append(file_name)

    cumulative_file.write(CUMULATIVE_TEMPLATE.replace('$file_template', changelog_file_text))
    cumulative_file.close()
    return changelog_file_names_list


def create_change_set_files(properties: Properties, change_set_file_names_list: list, liquibase_dir_path: str):
    if properties.has_new_roles():
        create_change_set_file(liquibase_dir_path,
                               get_file_name_contains_from_list('role', 'to', change_set_file_names_list), properties,
                               MODE_ROLE)

    if properties.has_new_authorities():
        create_change_set_file(liquibase_dir_path,
                               get_file_name_contains_from_list('authorit', 'to', change_set_file_names_list),
                               properties, MODE_AUTHORITY)

    if properties.has_new_users():
        create_change_set_file(liquibase_dir_path,
                               get_file_name_contains_from_list('user', 'to', change_set_file_names_list), properties,
                               MODE_USER)

    if properties.has_new_authorities_to_roles():
        create_change_set_file(liquibase_dir_path, get_file_name_contains_from_list('authorities_to_roles', '%',
                                                                                    change_set_file_names_list),
                               properties, MODE_AUTHORITIES_TO_ROLES)

    if properties.has_new_users_to_roles():
        create_change_set_file(liquibase_dir_path,
                               get_file_name_contains_from_list('users_to_roles', '%', change_set_file_names_list),
                               properties, MODE_USERS_TO_ROLES)


def get_file_name_contains_from_list(file_name_contains: str, file_name_not_contains: str,
                                     file_names_list: list) -> str:
    for file_name in file_names_list:
        if file_name_contains in file_name and file_name_not_contains not in file_name:
            return file_name
    raise ValueError(f'There is no file contains "{file_name_contains}" in list: {file_names_list}')


def create_change_set_file(liquibase_dir_path: str, file_name: str, properties: Properties, mode: int):
    change_set_file_path = f'{liquibase_dir_path}/{file_name}'
    change_set_file = open(change_set_file_path, "w")

    if mode == MODE_ROLE:
        sql = create_role_sql(properties)
        context = properties.roles_context
        change_set_file.write(CHANGE_SET_TEMPLATE.replace(CONTEXT_CONSTANT, context).replace(CHANGE_SET_CONSTANT, sql))

    if mode == MODE_AUTHORITY:
        sql = create_authority_sql(properties)
        context = properties.authorities_context
        change_set_file.write(CHANGE_SET_TEMPLATE.replace(CONTEXT_CONSTANT, context).replace(CHANGE_SET_CONSTANT, sql))

    if mode == MODE_USER:
        sql = create_user_sql(properties)
        context = properties.users_context
        change_set_file.write(CHANGE_SET_TEMPLATE.replace(CONTEXT_CONSTANT, context).replace(CHANGE_SET_CONSTANT, sql))

    if mode == MODE_AUTHORITIES_TO_ROLES:
        sql = create_authorities_to_roles_sql(properties)
        context = properties.authorities_to_roles_context
        change_set_file.write(CHANGE_SET_TEMPLATE.replace(CONTEXT_CONSTANT, context).replace(CHANGE_SET_CONSTANT, sql))

    if mode == MODE_USERS_TO_ROLES:
        sql = create_users_to_roles_sql(properties)
        context = properties.users_to_roles_context
        change_set_file.write(CHANGE_SET_TEMPLATE.replace(CONTEXT_CONSTANT, context).replace(CHANGE_SET_CONSTANT, sql))

    change_set_file.close()


def create_role_sql(properties: Properties) -> str:
    sql_query_list = []
    roles = properties.roles
    role_names = []

    for role in roles:
        role_names.append(role.name)
        sql_query_list.append(
            SQL_ROLE_CREATION_TEMPLATE.replace(NAME_CONSTANT, role.name).replace('$DESCRIPTION', role.description))
        sql_query_list.append('')

    sql_query_list.append(SQL_NEW_REVISION_RECORD)
    sql_query_list.append('')

    for role in roles:
        sql_query_list.append(SQL_ROLE_AUDIT_TEMPLATE.replace(NAME_CONSTANT, role.name))
        sql_query_list.append('')

    sql_query = '\n'.join(sql_query_list[:-1])
    comment = f'Add new role{"s" if len(role_names) > 1 else ""}: {", ".join(role_names)}'
    change_set_name = f'{properties.date}_001_new_role{"s" if len(role_names) > 1 else ""}'
    return CHANGE_SET_SQL_TEMPLATE.replace('$sql', sql_query).replace(COMMENT_CONSTANT, comment) \
        .replace(AUTHOR_CONSTANT, properties.author).replace(CHANGE_SET_NAME_CONSTANT, change_set_name)


def create_authority_sql(properties: Properties) -> str:
    authorities = properties.authorities
    sql_query_list = []
    authority_names = []

    add_authorities_in_sql_query_list(authorities, authority_names, sql_query_list)

    sql_query_list.append(SQL_NEW_REVISION_RECORD)
    sql_query_list.append('')

    add_audit_in_authorities_sql_query_list(authorities, sql_query_list)

    sql_query = '\n'.join(sql_query_list[:-1])
    comment = f'Add new authorit{"ies" if len(authority_names) > 1 else "y"}: {", ".join(authority_names)}'
    change_set_name = f'{properties.date}_001_new_authorit{"ies" if len(authority_names) > 1 else "y"}'
    return CHANGE_SET_SQL_TEMPLATE.replace('$sql', sql_query).replace(COMMENT_CONSTANT, comment) \
        .replace(AUTHOR_CONSTANT, properties.author).replace(CHANGE_SET_NAME_CONSTANT, change_set_name)


def create_user_sql(properties: Properties) -> str:
    users = properties.users
    sql_query_list = []
    usernames = []

    add_users_in_sql_query_list(sql_query_list, usernames, users)

    sql_query_list.append(SQL_NEW_REVISION_RECORD)
    sql_query_list.append('')

    add_audit_in_users_sql_query_list(sql_query_list, users)

    sql_query = '\n'.join(sql_query_list[:-1])
    comment = f'Add new user{"s" if len(usernames) > 1 else ""}: {", ".join(usernames)}'
    change_set_name = f'{properties.date}_001_new_user{"s" if len(usernames) > 1 else ""}'
    return CHANGE_SET_SQL_TEMPLATE.replace('$sql', sql_query).replace(COMMENT_CONSTANT, comment) \
        .replace(AUTHOR_CONSTANT, properties.author).replace(CHANGE_SET_NAME_CONSTANT, change_set_name)


def create_authorities_to_roles_sql(properties: Properties) -> str:
    authorities_to_roles_list = properties.authorities_to_roles
    sql_query_list = []
    authority_names = []

    add_authorities_to_roles_in_sql_query_list(authorities_to_roles_list, authority_names, sql_query_list)

    sql_query_list.append(SQL_NEW_REVISION_RECORD)
    sql_query_list.append('')

    add_audit_in_authorities_roles_sql_query_list(authorities_to_roles_list, sql_query_list)

    sql_query = '\n'.join(sql_query_list[:-1])
    comment = 'Add new link between roles and authorities'
    change_set_name = f'{properties.date}_001_new_link_between_roles_and_authorities'
    return CHANGE_SET_SQL_TEMPLATE.replace('$sql', sql_query).replace(COMMENT_CONSTANT, comment) \
        .replace(AUTHOR_CONSTANT, properties.author).replace(CHANGE_SET_NAME_CONSTANT, change_set_name)


def create_users_to_roles_sql(properties: Properties) -> str:
    users_to_roles_list = properties.users_to_roles
    sql_query_list = []
    usernames = []

    add_users_to_roles_in_sql_query_list(sql_query_list, usernames, users_to_roles_list)

    sql_query_list.append(SQL_NEW_REVISION_RECORD)
    sql_query_list.append('')

    add_audit_in_users_to_roles_sql_query_list(sql_query_list, users_to_roles_list)

    sql_query = '\n'.join(sql_query_list[:-1])
    comment = 'Add new link between roles and users'
    change_set_name = f'{properties.date}_001_new_link_between_roles_and_authorities'
    return CHANGE_SET_SQL_TEMPLATE.replace('$sql', sql_query).replace(COMMENT_CONSTANT, comment) \
        .replace(AUTHOR_CONSTANT, properties.author).replace(CHANGE_SET_NAME_CONSTANT, change_set_name)


def insert_vars_into_user_creation_template(user):
    return SQL_USER_CREATION_TEMPLATE \
        .replace('$ACCOUNT_NON_EXPIRED', '1' if user.account_non_expired else '0') \
        .replace('$ACCOUNT_NON_LOCKED', '1' if user.account_non_locked else '0') \
        .replace('$CREDENTIALS_NON_EXPIRED', '1' if user.credentials_non_expired else '0') \
        .replace('$ENABLED', '1' if user.enabled else '0') \
        .replace('$FIRST_NAME', user.first_name) \
        .replace('$LAST_NAME', user.last_name) \
        .replace('$MIDDLE_NAME', user.middle_name) \
        .replace('$PASSWORD', user.password) \
        .replace(USERNAME_CONSTANT, user.username) \
        .replace('$DOMAIN', user.domain) \
        .replace('$EMAIL', 'null' if user.email is None else f"'{user.email}'")


def add_authorities_in_sql_query_list(authorities, authority_names, sql_query_list):
    for authority in authorities:
        authority_names.append(authority.name)
        sql_query_list.append(SQL_AUTHORITY_CREATION_TEMPLATE
                              .replace(NAME_CONSTANT, authority.name)
                              .replace('$DESCRIPTION', authority.description))
        sql_query_list.append('')
        if authority.roles is not None and len(list(authority.roles)) > 0:
            for role in authority.roles:
                sql_query_list.append(SQL_AUTHORITY_TO_ROLE_CREATION_TEMPLATE.replace(ROLE_NAME_CONSTANT, role)
                                      .replace(AUTHORITY_NAME_CONSTANT, authority.name))
                sql_query_list.append('')


def add_users_in_sql_query_list(sql_query_list, usernames, users):
    for user in users:
        usernames.append(user.username)
        sql_query_list.append(insert_vars_into_user_creation_template(user))
        sql_query_list.append('')
        if user.roles is not None and len(list(user.roles)) > 0:
            for role in user.roles:
                sql_query_list.append(SQL_USER_TO_ROLE_TEMPLATE.replace(ROLE_NAME_CONSTANT, role)
                                      .replace(USERNAME_CONSTANT, user.username))
                sql_query_list.append('')


def add_authorities_to_roles_in_sql_query_list(authorities_to_roles_list: list[AuthoritiesToRoles],
                                               authority_names: list,
                                               sql_query_list: list):
    for authorities_roles in authorities_to_roles_list:
        for authority in authorities_roles.authorities:
            authority_names.append(authority)
            for role in authorities_roles.to_roles:
                sql_query_list.append(SQL_AUTHORITY_TO_ROLE_CREATION_TEMPLATE.replace(ROLE_NAME_CONSTANT, role)
                                      .replace(AUTHORITY_NAME_CONSTANT, authority))
                sql_query_list.append('')


def add_users_to_roles_in_sql_query_list(sql_query_list: list, usernames: list,
                                         users_to_roles_list: list[UsersToRoles]):
    for users_roles in users_to_roles_list:
        for username in users_roles.users:
            usernames.append(username)
            for role in users_roles.to_roles:
                sql_query_list.append(SQL_USER_TO_ROLE_TEMPLATE.replace(ROLE_NAME_CONSTANT, role)
                                      .replace(USERNAME_CONSTANT, username))
                sql_query_list.append('')


def add_audit_in_authorities_roles_sql_query_list(authorities_to_roles_list: list[AuthoritiesToRoles],
                                                  sql_query_list: list):
    for authorities_roles in authorities_to_roles_list:
        for authority in authorities_roles.authorities:
            for role in authorities_roles.to_roles:
                sql_query_list.append(SQL_AUTHORITY_TO_ROLE_AUDIT_TEMPLATE.replace(ROLE_NAME_CONSTANT, role)
                                      .replace(AUTHORITY_NAME_CONSTANT, authority))
                sql_query_list.append('')


def add_audit_in_users_sql_query_list(sql_query_list, users):
    for user in users:
        sql_query_list.append(SQL_USER_AUDIT_TEMPLATE.replace(USERNAME_CONSTANT, user.username))
        sql_query_list.append('')
        if user.roles is not None and len(list(user.roles)) > 0:
            for role in user.roles:
                sql_query_list.append(SQL_USER_TO_ROLE_AUDIT_TEMPLATE.replace(ROLE_NAME_CONSTANT, role)
                                      .replace(USERNAME_CONSTANT, user.username))
                sql_query_list.append('')


def add_audit_in_authorities_sql_query_list(authorities, sql_query_list):
    for authority in authorities:
        sql_query_list.append(SQL_AUTHORITY_AUDIT_TEMPLATE.replace('$NAME', authority.name))
        sql_query_list.append('')
        if authority.roles is not None and len(list(authority.roles)) > 0:
            for role in authority.roles:
                sql_query_list.append(SQL_AUTHORITY_TO_ROLE_AUDIT_TEMPLATE.replace(ROLE_NAME_CONSTANT, role)
                                      .replace(AUTHORITY_NAME_CONSTANT, authority.name))
                sql_query_list.append('')


def add_audit_in_users_to_roles_sql_query_list(sql_query_list: list, users_to_roles_list: list[UsersToRoles]):
    for users_roles in users_to_roles_list:
        for username in users_roles.users:
            for role in users_roles.to_roles:
                sql_query_list.append(SQL_USER_TO_ROLE_AUDIT_TEMPLATE.replace(ROLE_NAME_CONSTANT, role)
                                      .replace(USERNAME_CONSTANT, username))
                sql_query_list.append('')


def run():
    print(START_INFO)
    yml_path = check_args_and_get_yml_path()
    with open(yml_path, 'r') as stream:
        try:
            properties = Properties(yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)

    if not properties.has_new_data_in_properties():
        print('There is no data in yml file to create liquibase scripts')
        exit(0)

    liquibase_dir_path = create_dir(properties)
    change_set_file_names_list = create_cumulative_file(liquibase_dir_path, properties)
    create_change_set_files(properties, change_set_file_names_list, liquibase_dir_path)

    print(f'Successful creation of the new files: {", ".join(change_set_file_names_list)} in {liquibase_dir_path}')
    print(f'Don\'t forget to add cumulative.xml file to db.changelog.xml')


run()
