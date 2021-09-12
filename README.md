# Liquibase Python Person Generator
Quick way to create multiple liquibase scripts via python.

---
## Content
1. [Installation](#installation)
2. [Usage](#usage)
3. [Table fields info](#table-fields-info)
   1. [First level fields](#first-level-fields)
   2. [Second level fields](#second-level-fields)
      1. [New roles list](#new-roles-list)
      2. [New authorities list](#new-authorities-list)
      3. [New users list](#new-users-list)
   3. [Third level fields](#third-level-fields)
      1. [Roles list](#roles-list)
      2. [Authorities list](#authorities-list)
      3. [Users list](#users-list)
4. [Misc](#misc)
   1. [Example of .yml file](#example-of-yml-file)
   2. [Additional notes](#additional-notes)

---
## Installation
Install [Python > 3.9](https://www.python.org/).  
Additional libraries can be installed in terminal by `pip install <library_name>`.

Back to [content](#content).
## Usage
1. `python3 liquibase_person_generator.py <yml_absolute_path>` – create scripts in working dir.
2. `python3 liquibase_person_generator.py createExample` – create example .yml file in working dir.  

Back to [content](#content).
## Table fields info
### First level fields
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| version | Liquibase scripts version | String | 5.5.9 | Yes | 
| date | Liquibase scripts date | String | 2021-07-23 | Yes |
| author | Liquibase scripts author | String | Test Testovich | Yes |
| new-roles | New roles to add | List | _See new roles list fields info_ | No |
| new-authorities | New authorities to add | List | _See new authorities list fields info_ | No |
| new-users | New users to add | List | _See new users list fields info_ | No |

Back to [content](#content).
### Second level fields
#### New roles list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| context | Liquibase scripts context | String | production,list | Yes | 
| roles | New roles list | List | _See roles list fields info_ | Yes |

Back to [content](#content).
#### New authorities list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| context | Liquibase scripts context | String | production,list | Yes | 
| authorities | New authorities list | List | _See authorities list fields info_ | Yes |

Back to [content](#content).
#### New users list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| context | Liquibase scripts context | String | production,list | Yes | 
| users | New users list | List | _See users list fields info_ | Yes |

Back to [content](#content).
### Third level fields
#### Roles list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| name | Role name | String | TEST_ROLE | Yes |
| description | Role description | String | Role test description | Yes |

Back to [content](#content).
#### Authorities list
| Field name | Info | Field type | Example | Required |
| --- | --- | --- | --- | --- |
| name | Authority name | String | test_authority | Yes |
| description | Authority description | String | Authority test description | Yes |
| roles | The list of roles to which you want to bind authority | List of strings (role names) | - TEST_ROLE<br/>- DEVELOPER  | No |

Back to [content](#content).
#### Users list
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
## Misc
### Example of .yml file
In the following example, scripts will be created in which:
* role with name `TEST` will be created in `production` and `test` context
* authorities with names `test_authority_1` and `test_authority_2` will be created, and `test_authority_2` will be linked with roles `DEVELOPER` and `TEST` in `test` context
* users with usernames `ivan_ivanov` and `petr_petrov` will be created and linked with relevant roles in `production` and `test` context
```yml
version: 5.25.0
date: 2021-07-23
author: Test Testovich

new-roles:
  context: production,test
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
  context: production,test
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
```

Back to [content](#content).
### Additional notes
Don't forget to add info of liquibase scripts in `db.changelog.xml` file!

Back to [content](#content).