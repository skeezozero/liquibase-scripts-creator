import os
import sys
import yaml

START_INFO = '''
Liquibase Person Generator v 1.0.0 by Sk33z0
'''
HELP_INFO = '''Specify yml absolute path with parameters.

Example: liquibase_person_generator.py --yml-file-name=C://script/example.yml'''
CUMULATIVE_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
        xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog ../dbchangelog-3.5.xsd"
        context="$context">

$file_template

</databaseChangeLog>
'''
CUMULATIVE_CHANGELOG_TEMPLATE = '    <include file="$file_name" relativeToChangelogFile="true"/>'
# todo change context to every changelog
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

# todo change context to every creation
class Properties:

    def __init__(self, yml_properties: dict):
        self.version = yml_properties['version']
        self.date = str(yml_properties['date']).replace('-', '')
        self.author = yml_properties['author']
        self.context = yml_properties['context']
        self.users = []
        for user in yml_properties['new-users']:
            self.users.append(User(user))


def get_yml_path() -> str:
    args = sys.argv
    if len(args) != 2:
        print('Arguments Error')
        print(HELP_INFO)
        exit(1)
    return str(args[1]).split('=')[1]


def create_dir(properties: Properties) -> str:
    dir_path = f'{os.getcwd()}/v-{properties.version}'
    os.mkdir(dir_path)
    return dir_path


# todo add roles/authorities
def create_cumulative_file(liquibase_dir_path: str, properties: Properties):
    cumulative_file_path = f'{liquibase_dir_path}/changelog-v{properties.version}_cumulative.xml'
    cumulative_file = open(cumulative_file_path, "w")
    cumulative_file_changelogs = CUMULATIVE_CHANGELOG_TEMPLATE.replace('$file_name',
                                                                       f'{properties.date}_001_new_users.xml')
    cumulative_file_text = CUMULATIVE_TEMPLATE.replace('$file_template', cumulative_file_changelogs)
    cumulative_file.write(cumulative_file_text)
    cumulative_file.close()

# todo set change set file paths as args
def create_user_change_set(liquibase_dir_path: str, properties: Properties):
    change_set_file_path = f'{liquibase_dir_path}/{properties.date}_001_new_users.xml'
    change_set_file = open(change_set_file_path, "w")

    user_sql_list = []
    for user in properties.users:
        user_sql_list.append(user)
    sql = '\n'.join(list(map(str, user_sql_list)))

    change_set_file.write(CHANGE_SET_TEMPLATE.replace('$context', properties.context).replace('$change_set', sql))
    change_set_file.close()


def create_user_sql(user: User) -> str:



def run():
    print(START_INFO)
    yml_path = get_yml_path()
    with open(yml_path, 'r') as stream:
        try:
            properties = Properties(yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)
    liquibase_dir_path = create_dir(properties)
    create_cumulative_file(liquibase_dir_path, properties)


run()
