# admintools
GSoC 2017 Data Quality &amp; Admin Tools

[![Build Status](https://travis-ci.org/openstates/admintools.svg?branch=master)](https://travis-ci.org/openstates/admintools)


# Open States Admin Tools Documentation

1. [Management Commands](#management-commands)
2. [Django Views](#django-views)
3. [Helper Functions](#helper-functions)

---
## Management Commands
1. Import Data Quality Issues into Database
    ```
    python manage.py import
    python manage.py import --people
    python manage.py import --organizations
    python manage.py import --membership
    python manage.py import --posts
    python manage.py import --vote_events
    python manage.py import --bills
    ```
    > provide optional arguments to import specific type of data quality issues

2. Import People Related Issue Resolver Patches into Database
    ```
    python manage.py resolve
    ```
---
## Django Views
1. [Status Page](#status-page)
2. [Jurisdiction Specific Page](#jurisdiction-specific-page)
3. [Legislative Session Info Page](#legislative-session-info-page)    
4. [List Data Quality Issues](#list-data-quality-issues)
5. [Person Resolve Issues](#person-resolve-issues)
6. [Review Person Patches](#review-person-patches)
7. [List All Person Patches](#list-all-person-patches)
8. [Retire Legislators](#retire-legislators)
9. [List Retired Legislators](#list-retired-legislators)
10. [Name Resolution Tool](#name-resolution-tool)
11. [Create Person Patch](#create-person-patch)
12. [Data Quality Exceptions](#data-quality-exceptions)

---

## Helper Functions
1. [_get_run_status](#status-page)
2. [_validate_date](#validate-date)
3. [_get_url_slug](#get-url-slug)
4. [_get_pagination](#get-pagination)
5. [_jur_dataquality_issues](#jurisdiction-specific-page)
6. [_filter_results](#filter-results)
7. [_prepare_import](#person-resolve-issues)

---
### Status Page

**View Name**:- `overview`

**Purpose**:- Displays the status of all known data quality issues and run details for all jurisdictions in a tabular format.

**Helper Function**:-
1. `_get_run_status`:- This function calculates the Run Status of a given jurisdiction. which returns

    `{'count': VALUE , 'date': DATE}`

        Where,
            1. VALUE:-  None (if only last run failed)
                        0 (if last run was successful)
                        X (last X runs failed, where X > 1)
            2. DATE:- Last Run Date (datetime.date(YYYY, MM, DD))            

Data Format Used to Display the Information:-
```
[('jurisdiction_id',
    {'issue_related_class': {'alert': count_of_issues},
     'run': _get_run_status})]
```
Where, *issue_related_class* :- `IssueType.class_for(issue_slug)` ie, name of opencivicdata model class which belongs to issue.

---

### Jurisdiction Specific Page

**View Name**:- `jurisdiction_intro`

**Purpose**:-
1. Displays Jurisdiction Specific Information like,
    1. Data Quality Issues
    2. Data Quality Exceptions
2. Provide links to different tools like,
    1. Merge Tool
    2. Name Resolution Tool
        - Bill Sponsors
        - Voters
        - Memberships
    3. Retirement Tool    

**Helper Function**:-
1. `_jur_dataquality_issues`:- This function returns `Data Quality Issues` and `Data Quality Exceptions` related information in below format
    ```
    {related_class: {issue_slug: {'alert': ALERT,
                                  'count': COUNT,
                                  'description': DESCRIPTION }}}
    ```
    Where,
    - related_class = name of opencivicdata model class which belongs to issue
    - issue_slug = issue_slug of a issue
    - ALERT
        - True = If issue is of type `error`
        - False = If issue is of type `warning`
    - COUNT = count of number of issues
    - DESCRIPTION = description about a issue `IssueType.description_for(issue_slug)`

---

### Legislative Session Info Page

**View Name**:- `legislative_session_info`

**Purpose**:- Displays Jurisdiction Specific Bills and VoteEvents related information for a session.

---

### List Data Quality Issues

**View Name**:- `list_issue_objects`

**Purpose**:-
1. Displays Information about jurisdiction specific Data Quality Issues for **Particular Issue**
2. Give User functionality to ignore selected data quality issues ie, to mark them as `data quality exceptions`
3. User can filter objects by making queries.

**Helper Functions**:-
- [_filter_results](#filter-results)
- [_get_pagination](#get-pagination)
- [_get_url_slug](#get-url-slug)

---

### Person Resolve Issues

**View Name**:- `person_resolve_issues`

**Purpose**:- Allows user to create `unreviewed` person patches for `missing` values (ie, `alert=warning`) which will be applied_by `admin`. User can create person-patches from `Data Quality Section`.

**Helper Function**:-
1. `_prepare_import`:- This function processes the data posted by user from `Data Quality Section` and format data in below format:-
    - Let's posted data via form is
    ```
    {'1_ocd-person/36712942-a037-453d-bc1e-8b69b2b9fc3a': 'hiteshgarg@gmail.com',
    'note_1_ocd-person/36712942-a037-453d-bc1e-8b69b2b9fc3a': 'capitol office',

    'ocd-person/36712942-a037-453d-bc1e-8b69b2b9fc3a': 'garghitesh95@gmail.com',   
    'note_ocd-person/36712942-a037-453d-bc1e-8b69b2b9fc3a': 'district office',

    'csrfmiddlewaretoken': 'hApnoKiiT7qsdpnjTOi6PDH0jjOvdUP9WYVtUwJxfJN3SGfbkMM5hvIU6C71c8F9',

    'note_ocd-person/4312e721-ea50-4390-89bc-ff0c03a5a932': 'capitol office',
    'ocd-person/4312e721-ea50-4390-89bc-ff0c03a5a932': 'test@gmail.com'}

    ```
    - Then data returned from `_perpare_import` will be
    ```
    {'1__@#$__test@gmail.com': {'code': '',
                                 'id': 'ocd-person/4312e721-ea50-4390-89bc-ff0c03a5a932',
                                 'note': 'capitol office'},
     '2__@#$__garghitesh95@gmail.com': {'code': '1_',
                                  'id': 'ocd-person/36712942-a037-453d-bc1e-8b69b2b9fc3a',
                                  'note': 'capitol office'},
     '3__@#$__hiteshgarg@gmail.com': {'code': '',
                                 'id': 'ocd-person/36712942-a037-453d-bc1e-8b69b2b9fc3a',
                                 'note': 'district office'}})
    ```
    Here, *__@#$__* and **_code_** are used to extract data into `person_resolve_issues` view


---

### Review Person Patches

**View Name**:- `review_person_patches`

**Purpose**:-
- lists `unreviewed` person patches for review
- User can mark a patch as `approved` and `rejected`
- Allows User to filter results by `Category`, `Alert`, `Created By` and `Person Name`
- Posted Data via form will be of below format
    - Key = `category__patch_id__object_id`
    - Value = `status`
- If there is a `approved` patch for `image` or `name`. Then it also mark previously `approved` patch as `deprecated`.

**Helper Function**:-
- [_get_pagination](#get-pagination)
---

### List All Person Patches

**View Name**:- `list_all_person_patches`

**Purpose**:-
- lists all person patches for a jurisdiction
- Allows User to filter results by `Category`, `Alert`, `Created By`, `Status` and `Person Name`
- Allows User to update the `Status` of a patch
- if category is `name` or `image` and updated status is `approved`. Then it makes sure to display error if there is already a `approved` patch present for an object

**Helper Function**:-
- [_get_pagination](#get-pagination)
---

### Retire Legislators

**View Name**:- `retire_legislators`

**Purpose**:-
- Lists all unretired legislators of a jurisdiction.
- Allows user to enter retirement dates of legislators and bulk retire them.
- Make sure that provided retirement date is not less than all of the existing membership `end_dates`. If so then displays the error.
- Allows User to search a legislator by name
- Make sure to validate date provided by user in `YYYY-MM-DD` format

**Helper Functions**:-
- [_get_pagination](#get-pagination)
- [_validate_date](#validate-date)

---

### List Retired Legislators

**View Name**:- `list_retired_legislators`

**Purpose**:-
- Lists all retired legislators of a jurisdiction.
- Allows user to update retirement dates of legislators and bulk update them.
- Make sure that provided retirement date is not less than the membership `end_date`(other than current `retirement date`)
- Allows User to search a legislator by name
- Make sure to validate date provided by user in `YYYY-MM-DD` format

**Helper Functions**:-
- [_get_pagination](#get-pagination)
- [_validate_date](#validate-date)

---

### Name Resolution Tool

**View Name**:- `name_resolution_tool`

**Purpose**:-
- Allows User to Match
    - Unmatched Bill Sponsors
    - Unmatched Voters
    - Unmatched Organization Members

  with related `person` object.
- Users can filter legislators according to legislative session

**Helper Function**:-
- [_get_pagination](#get-pagination)        

---

### Create Person Patch

**View Name**:- `create_person_patch`

**Purpose**:- Allows User to create a `person-patch` for *wrong values*(ie, alert type is `error`) on openstates.org with status of `unreviewed`

---

### Data Quality Exceptions

**View Name**:- `dataquality_exceptions`

**Purpose**:-
- Allows User to mark a data quality issues as `ignored` from `Data Quality Issue Section` (in this case Django-view will take `action='add'` as argument)
- Allows User to remove data quality issues which are marked as `ignored` (in this case Django-view will take `action='remove'` as argument)
- Lists all ignored data quality issues for a jurisdiction
- Allows User to filter results.


**Helper Function**:-
- [_get_pagination](#get-pagination)   
- [_get_url_slug](#get-url-slug)
- [_filter_results](#filter-results)

---
### Common Helper Functions

#### Filter Results

- **Function Name**:- `_filter_results`

- **Purpose**:- Filter the objects according to query of user


#### Get Pagination

- **Function Name**:- `_get_pagination`

- **Purpose**:- Paginate the objects (20 objects per page)


#### Get URL Slug

- **Function Name**:- `_get_url_slug`

- **Purpose**:- To links objects to related Django-admin page. It returns a string according to `related_class`.
It follows pattern:- `app_label_related_class_change`

    Where,
     - app_label = core/legislative
     - related_class = issue related class
 

#### Validate Date

- **Function Name**:- `_validate_date`

- **Purpose**:- validate date in `YYYY-MM-DD` format
