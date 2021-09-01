import os
import sys
import yaml

MODE_ROLE = 1
MODE_AUTHORITY = 2
MODE_USER = 3
START_INFO = '''
Liquibase Script Generator v 1.0.0 by Skeezo
'''
HELP_INFO = '''Specify yml absolute path with parameters.

Example: liquibase_person_generator.py --yml-file-name=C://script/example.yml'''
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
SQL_ROLE_AUDIT_TEMPLATE = '''            insert into ROLE_AUDIT(REVISION_ID, REVISION_TYPE, NAME, DESCRIPTION)
            select (select max(REVISION_ID) from REVISION_INFO), 0, NAME, DESCRIPTION
            from ROLE
            where NAME = '$NAME';'''
SQL_AUTHORITY_CREATION_TEMPLATE = '''            insert into AUTHORITY(NAME, DESCRIPTION) values ('$NAME', '$DESCRIPTION');'''
SQL_AUTHORITY_AUDIT_TEMPLATE = '''            insert into AUTHORITY_AUDIT(REVISION_ID, REVISION_TYPE, NAME, DESCRIPTION)
            select (select max(REVISION_ID) from REVISION_INFO), 0, NAME, DESCRIPTION
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
        self.roles = person['roles']


class Authority:

    def __init__(self, authority: dict):
        self.name = authority['name']
        self.description = authority['description']
        self.roles = authority['roles']


class Role:

    def __init__(self, role: dict):
        self.name = role['name']
        self.description = role['description']


class Properties:

    def __init__(self, yml_properties: dict):
        self.version = yml_properties['version']
        self.date = str(yml_properties['date']).replace('-', '')
        self.author = yml_properties['author']

        self.roles_context = yml_properties['new-roles']['context'] if yml_properties['new-roles'] is not None else None
        self.roles = []
        self.users_context = yml_properties['new-users']['context'] if yml_properties['new-users'] is not None else None
        self.users = []
        self.authorities_context = yml_properties['new-authorities']['context'] \
            if yml_properties['new-authorities'] is not None else None
        self.authorities = []

        if self.users_context is not None:
            for user in yml_properties['new-users']['users']:
                self.users.append(User(user))

        if self.roles_context is not None:
            for role in yml_properties['new-roles']['roles']:
                self.roles.append(Role(role))

        if self.authorities_context is not None:
            for authority in yml_properties['new-authorities']['authorities']:
                self.authorities.append(Authority(authority))

    def has_new_roles(self) -> bool:
        return self.roles is not None and self.roles_context is not None

    def has_new_authorities(self) -> bool:
        return self.authorities is not None and self.authorities_context is not None

    def has_new_users(self) -> bool:
        return self.users is not None and self.users_context is not None


def get_yml_path() -> str:
    args = sys.argv
    if len(args) != 2 or '--yml-file-name=' not in args[1]:
        print('Arguments Error')
        print(HELP_INFO)
        exit(1)
    return str(args[1]).split('=')[1]


def create_dir(properties: Properties) -> str:
    dir_path = f'{os.getcwd()}/v-{properties.version}'
    os.mkdir(dir_path)
    return dir_path


def create_cumulative_file(liquibase_dir_path: str, properties: Properties) -> list:
    cumulative_file_path = f'{liquibase_dir_path}/changelog-v{properties.version}_cumulative.xml'
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
        changelog_file_names_list.append(file_name)

    cumulative_file.write(CUMULATIVE_TEMPLATE.replace('$file_template', changelog_file_text))
    cumulative_file.close()
    return changelog_file_names_list


def create_change_set_file(liquibase_dir_path: str, file_name: str, properties: Properties, mode: int):
    change_set_file_path = f'{liquibase_dir_path}/{file_name}'
    change_set_file = open(change_set_file_path, "w")

    if mode == MODE_ROLE:
        sql = create_role_sql(properties)
        context = properties.roles_context
        change_set_file.write(CHANGE_SET_TEMPLATE.replace('$context', context).replace('$change_set', sql))

    if mode == MODE_AUTHORITY:
        sql = create_authority_sql(properties)
        context = properties.authorities_context
        change_set_file.write(CHANGE_SET_TEMPLATE.replace('$context', context).replace('$change_set', sql))

    if mode == MODE_USER:
        sql = create_user_sql(properties)
        context = properties.users_context
        change_set_file.write(CHANGE_SET_TEMPLATE.replace('$context', context).replace('$change_set', sql))

    change_set_file.close()


def create_role_sql(properties: Properties) -> str:
    sql_query_list = []
    roles = properties.roles
    role_names = []

    for role in roles:
        role_names.append(role.name)
        sql_query_list.append(
            SQL_ROLE_CREATION_TEMPLATE.replace('$NAME', role.name).replace('$DESCRIPTION', role.description))
        sql_query_list.append('')

    sql_query_list.append('            call NEW_REVISION_RECORD();')
    sql_query_list.append('')

    for role in roles:
        sql_query_list.append(SQL_ROLE_AUDIT_TEMPLATE.replace('$NAME', role.name))
        sql_query_list.append('')

    sql_query = '\n'.join(sql_query_list[:-1])
    comment = f'Add new roles: {", ".join(role_names)}'
    change_set_name = f'{properties.date}_001_new_roles'
    return CHANGE_SET_SQL_TEMPLATE.replace('$sql', sql_query).replace('$comment', comment) \
        .replace('$author', properties.author).replace('$change_set_name', change_set_name)


def create_authority_sql(properties: Properties) -> str:
    authorities = properties.authorities
    sql_query_list = []
    authority_names = []

    for authority in authorities:
        authority_names.append(authority.name)
        sql_query_list.append(SQL_AUTHORITY_CREATION_TEMPLATE
                              .replace('$NAME', authority.name)
                              .replace('$DESCRIPTION', authority.description))
        sql_query_list.append('')
        if authority.roles is not None and len(list(authority.roles)) > 0:
            for role in authority.roles:
                sql_query_list.append(SQL_AUTHORITY_TO_ROLE_CREATION_TEMPLATE.replace('$ROLE_NAME', role)
                                      .replace('$AUTHORITY_NAME', authority.name))
                sql_query_list.append('')

    sql_query_list.append('            call NEW_REVISION_RECORD();')
    sql_query_list.append('')

    for authority in authorities:
        sql_query_list.append(SQL_AUTHORITY_AUDIT_TEMPLATE.replace('$NAME', authority.name))
        sql_query_list.append('')
        if authority.roles is not None and len(list(authority.roles)) > 0:
            for role in authority.roles:
                sql_query_list.append(SQL_AUTHORITY_TO_ROLE_AUDIT_TEMPLATE.replace('$ROLE_NAME', role)
                                      .replace('$AUTHORITY_NAME', authority.name))
                sql_query_list.append('')

    sql_query = '\n'.join(sql_query_list[:-1])
    comment = f'Add new authorities: {", ".join(authority_names)}'
    change_set_name = f'{properties.date}_001_new_authorities'
    return CHANGE_SET_SQL_TEMPLATE.replace('$sql', sql_query).replace('$comment', comment) \
        .replace('$author', properties.author).replace('$change_set_name', change_set_name)


def create_user_sql(properties: Properties) -> str:
    users = properties.users
    sql_query_list = []
    usernames = []

    for user in users:
        usernames.append(user.username)
        sql_query_list.append(SQL_USER_CREATION_TEMPLATE
                              .replace('$ACCOUNT_NON_EXPIRED', '1' if user.account_non_expired else '0')
                              .replace('$ACCOUNT_NON_LOCKED', '1' if user.account_non_locked else '0')
                              .replace('$CREDENTIALS_NON_EXPIRED', '1' if user.credentials_non_expired else '0')
                              .replace('$ENABLED', '1' if user.enabled else '0')
                              .replace('$FIRST_NAME', user.first_name)
                              .replace('$LAST_NAME', user.last_name)
                              .replace('$MIDDLE_NAME', user.middle_name)
                              .replace('$PASSWORD', user.password)
                              .replace('$USERNAME', user.username)
                              .replace('$DOMAIN', user.domain)
                              .replace('$EMAIL', 'null' if user.email is None else f"'{user.email}'"))
        sql_query_list.append('')
        if user.roles is not None and len(list(user.roles)) > 0:
            for role in user.roles:
                sql_query_list.append(SQL_USER_TO_ROLE_TEMPLATE.replace('$ROLE_NAME', role)
                                      .replace('$USERNAME', user.username))
                sql_query_list.append('')

    sql_query_list.append('            call NEW_REVISION_RECORD();')
    sql_query_list.append('')

    for user in users:
        sql_query_list.append(SQL_USER_AUDIT_TEMPLATE.replace('$USERNAME', user.username))
        sql_query_list.append('')
        if user.roles is not None and len(list(user.roles)) > 0:
            for role in user.roles:
                sql_query_list.append(SQL_USER_TO_ROLE_AUDIT_TEMPLATE.replace('$ROLE_NAME', role)
                                      .replace('$USERNAME', user.username))
                sql_query_list.append('')

    sql_query = '\n'.join(sql_query_list[:-1])
    comment = f'Add new users: {", ".join(usernames)}'
    change_set_name = f'{properties.date}_001_new_users'
    return CHANGE_SET_SQL_TEMPLATE.replace('$sql', sql_query).replace('$comment', comment) \
        .replace('$author', properties.author).replace('$change_set_name', change_set_name)


def has_new_data_in_properties(properties: Properties) -> bool:
    return properties.has_new_users() or properties.has_new_roles() or properties.has_new_authorities()


def get_file_name_contains_from_list(file_name_contains: str, file_names_list: list) -> str:
    for file_name in file_names_list:
        if file_name_contains in file_name:
            return file_name
    raise ValueError(f'There is no file contains "{file_name_contains}" in list: {file_names_list}')


def create_change_set_files(properties: Properties, change_set_file_names_list: list, liquibase_dir_path: str):
    if properties.has_new_roles():
        create_change_set_file(liquibase_dir_path, get_file_name_contains_from_list('role', change_set_file_names_list),
                               properties, MODE_ROLE)

    if properties.has_new_authorities():
        create_change_set_file(liquibase_dir_path,
                               get_file_name_contains_from_list('authorities', change_set_file_names_list),
                               properties, MODE_AUTHORITY)

    if properties.has_new_users():
        create_change_set_file(liquibase_dir_path, get_file_name_contains_from_list('user', change_set_file_names_list),
                               properties, MODE_USER)


def run():
    print(START_INFO)
    yml_path = get_yml_path()
    with open(yml_path, 'r') as stream:
        try:
            properties = Properties(yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)

    if not has_new_data_in_properties(properties):
        print('There is no data in yml file to create liquibase scripts')
        exit(0)

    liquibase_dir_path = create_dir(properties)
    change_set_file_names_list = create_cumulative_file(liquibase_dir_path, properties)
    create_change_set_files(properties, change_set_file_names_list, liquibase_dir_path)

    print(f'Successful creation of the new files: {", ".join(change_set_file_names_list)} in {liquibase_dir_path}')
    print(f'Don\'t forget to add cumulative.xml file to db.changelog.xml')


run()
