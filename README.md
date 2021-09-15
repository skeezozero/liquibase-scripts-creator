# Liquibase Python Scripts Generator
Quick way to create multiple liquibase scripts via python.  

![https://img.shields.io/badge/Version-1.1.0-green](https://img.shields.io/badge/Version-1.1.0-green)

## Content
1. [Installation](#installation)
2. [Version info](#version-info)
3. [Usage](#usage)
4. [Example of .yml file](#example-of-yml-file)
5. [Table fields info](#table-fields-info)
   1. [First level fields](#first-level-fields)
   2. [Second level fields](#second-level-fields)
      1. [New roles list](#new-roles-list)
      2. [New authorities list](#new-authorities-list)
      3. [New users list](#new-users-list)
      4. [Authorities to roles list](#authorities-to-roles-list)
      5. [Users to roles list](#users-to-roles-list)
   3. [Third level fields](#third-level-fields)
      1. [Roles list](#roles-list)
      2. [Authorities list](#authorities-list)
      3. [Users list](#users-list)
      4. [Authorities to roles link list](#authorities-to-roles-link-list)
      5. [users to roles link list](#users-to-roles-link-list)

---
## Version info
1. **v 1.0.0** – feature to save new roles/authorities/users.
2. **v 1.1.0** - feature to link existing authorities/users to roles.

Back to [content](#content).
## Installation
1. Install [Python > 3.9](https://www.python.org/).  
2. Additional libraries can be installed in terminal by `pip install <library_name>`.

Back to [content](#content).
## Usage
Script options:
1. `python3 liquibase_script_generator.py <yml_absolute_path>` – create scripts in working dir.
2. `python3 liquibase_script_generator.py createExample` – create example `.yml` file in working dir.

By configuring `.yml` file script will create liquibase scripts for new users/roles/authorities or link 
users/authorities with existing roles.  
<details>
<summary>File hierarchy example ...</summary>

File hierarchy after using command `python3 liquibase_script_generator.py <yml_absolute_path>` with `example_yml_file.yml`:
```
<working dir>
├── ...
├── liquibase_script_generator.py
└── v-5.6.0
    ├── 20210723_001_DML_roles.xml
    ├── 20210723_002_DML_authorities.xml
    ├── 20210723_003_DML_users.xml
    ├── 20210723_004_DML_authorities_to_roles.xml
    ├── 20210723_005_DML_users_to_roles.xml
    └── changelog-v-5.6.0_cumulative.xml
```
</details>

Back to [content](#content).
## Example of .yml file
Example of `.yml` file.  
Can be created by command `python3 liquibase_script_generator.py createExample`.
<details>
<summary>Description ...</summary>

In the following example, scripts will be created in which:
* new role with name `TEST` will be created in `production` and `test` context
* new authorities with names `test_authority_1` and `test_authority_2` will be created, and `test_authority_2` will be linked with roles `DEVELOPER` and `TEST` in `test` context
* new users with usernames `ivan_ivanov` and `petr_petrov` will be created and linked with relevant roles in `production` and `test` context
* existing authorities with names `existing_authority1` and `existing_authority2` will be linked with existing `DEVELOPER` role, existing authority with names `existing_authority3` will be linked with existing `DEVELOPER` and `TEST` roles in `test` context
* existing users with usernames `test_user1` and `test_user2` will be linked with existing `DEVELOPER` role, existing user with username `test_user3` will be linked with existing `DEVELOPER` and `TEST` roles in `production` and `test` context
</details>

```yml
version: 5.6.0
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
        - DEVELOPER
```

## Table fields info
## First level fields
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| version | Liquibase scripts version | String | 5.5.9 | Yes | 
| date | Liquibase scripts date | String | 2021-07-23 | Yes |
| author | Liquibase scripts author | String | Test Testovich | Yes |
| new-roles | New roles to add | List | _See new roles list fields info_ | No |
| new-authorities | New authorities to add | List | _See new authorities list fields info_ | No |
| new-users | New users to add | List | _See new users list fields info_ | No |
| authorities-to-roles | Create link between existing authorities and roles | List | _See authorities to roles list fields info_ | No |
| users-to-roles | Create link between existing users and roles | List | _See users to roles fields info_ | No |

Back to [content](#content).
## Second level fields
### New roles list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| context | Liquibase scripts context | List of strings | - production<br>- list | Yes | 
| roles | New roles list | List | _See roles list fields info_ | Yes |

Back to [content](#content).
### New authorities list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| context | Liquibase scripts context | List of strings | - production<br>- list | Yes | 
| authorities | New authorities list | List | _See authorities list fields info_ | Yes |

Back to [content](#content).
### New users list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| context | Liquibase scripts context | List of strings | - production<br>- list | Yes | 
| users | New users list | List | _See users list fields info_ | Yes |

Back to [content](#content).
### Authorities to roles list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| context | Liquibase scripts context | List of strings | - production<br>- list | Yes | 
| link | Link between existing authorities and roles | List | _See authorities to roles link fields info_ | Yes |

Back to [content](#content).
### Users to roles list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| context | Liquibase scripts context | List of strings | - production<br>- list | Yes | 
| link | Link between existing users and roles | List | _See users to roles link fields info_ | Yes |

Back to [content](#content).
## Third level fields
### Roles list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| name | Role name | String | TEST_ROLE | Yes |
| description | Role description | String | Role test description | Yes |

Back to [content](#content).
### Authorities list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| name | Authority name | String | test_authority | Yes |
| description | Authority description | String | Authority test description | Yes |
| roles | The list of roles to which you want to bind authority | List of strings (role names) | - TEST_ROLE<br/>- DEVELOPER  | No |

Back to [content](#content).
### Users list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| accountNonExpired | User account non expired | Boolean | true | Yes |
| accountNonLocked | User account non locked | Boolean | true | Yes |
| credentialsNonExpired | User account credentials non expired | Boolean | true | Yes |
| enabled | User account is enabled | Boolean | true | Yes |
| firstName | User account first name | String | Test | Yes |
| lastName | User account last name | String | Testov | Yes |
| middleName | User account middle name | String | Testovich | Yes |
| password | User account password | String | qwerty | Yes |
| username | User account username | String | test | Yes |
| domain | User account domain | String | DOMAIN.LOCALHOST | Yes |
| email | User account email | String | test@local.host | No |
| roles | The list of roles to which you want to bind user | List of strings (role names) | - TEST_ROLE<br/>- DEVELOPER  | No |

Back to [content](#content).
### Authorities to roles link list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| authorities | Authority names to link with roles | List of strings (authority names) | - existing_authority1<br>- existing_authority2 | Yes |
| to-roles | Role names to link with authorities | List of strings (role names) | - EXISTING_ROLE<br>- DEVELOPER | Yes |

Back to [content](#content).
### Users to roles link list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| usernames | Usernames to link with roles | List of strings (usernames) | - existing_username1<br>- existing_username2 | Yes |
| to-roles | Role names to link with usernames | List of strings (role names) | - EXISTING_ROLE<br>- DEVELOPER | Yes |

Back to [content](#content).