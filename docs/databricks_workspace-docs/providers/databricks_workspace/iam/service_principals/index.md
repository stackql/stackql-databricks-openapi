---
title: service_principals
hide_title: false
hide_table_of_contents: false
keywords:
  - Databricks
  - service_principals
  - iam
  - databricks_workspace
  - stackql
  - infrastructure-as-code
  - configuration-as-data
  - cloud inventory
description: Query, deploy and manage Databricks resources using SQL
custom_edit_url: null
image: /img/providers/databricks_workspace/stackql-databricks-provider-featured-image.png
---

import CopyableCode from '@site/src/components/CopyableCode/CopyableCode';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Operations on a <code>service_principals</code> resource.  

## Overview
<table><tbody>
<tr><td><b>Name</b></td><td><code>service_principals</code></td></tr>
<tr><td><b>Type</b></td><td>Resource</td></tr>
<tr><td><b>Id</b></td><td><CopyableCode code="databricks_workspace.iam.service_principals" /></td></tr>
</tbody></table>

## Fields
| Name | Datatype |
|:-----|:---------|
| <CopyableCode code="id" /> | `string` |
| <CopyableCode code="active" /> | `boolean` |
| <CopyableCode code="applicationId" /> | `string` |
| <CopyableCode code="displayName" /> | `string` |
| <CopyableCode code="entitlements" /> | `array` |
| <CopyableCode code="externalId" /> | `string` |
| <CopyableCode code="groups" /> | `array` |
| <CopyableCode code="roles" /> | `array` |
| <CopyableCode code="schemas" /> | `array` |

## Methods
| Name | Accessible by | Required Params | Description |
|:-----|:--------------|:----------------|:------------|
| <CopyableCode code="get" /> | `SELECT` | <CopyableCode code="id, deployment_name" /> | Gets the details for a single service principal define in the Databricks workspace. |
| <CopyableCode code="list" /> | `SELECT` | <CopyableCode code="deployment_name" /> | Gets the set of service principals associated with a Databricks workspace. |
| <CopyableCode code="create" /> | `INSERT` | <CopyableCode code="deployment_name" /> | Creates a new service principal in the Databricks workspace. |
| <CopyableCode code="delete" /> | `DELETE` | <CopyableCode code="id, deployment_name" /> | Delete a single service principal in the Databricks workspace. |
| <CopyableCode code="patch" /> | `UPDATE` | <CopyableCode code="id, deployment_name" /> | Partially updates the details of a single service principal in the Databricks workspace. |
| <CopyableCode code="update" /> | `UPDATE` | <CopyableCode code="id, deployment_name" /> | Updates the details of a single service principal. |

## `SELECT` examples

<Tabs
    defaultValue="list"
    values={[
        { label: 'service_principals (list)', value: 'list' },
        { label: 'service_principals (get)', value: 'get' }
    ]
}>
<TabItem value="list">

```sql
SELECT
id,
active,
applicationId,
displayName,
entitlements,
externalId,
groups,
roles,
schemas
FROM databricks_workspace.iam.service_principals
WHERE deployment_name = '{{ deployment_name }}';
```

</TabItem>
<TabItem value="get">

```sql
SELECT
id,
active,
applicationId,
displayName,
entitlements,
externalId,
groups,
roles,
schemas
FROM databricks_workspace.iam.service_principals
WHERE id = '{{ id }}' AND
deployment_name = '{{ deployment_name }}';
```

</TabItem>
</Tabs>

## `INSERT` example

Use the following StackQL query and manifest file to create a new <code>service_principals</code> resource.

<Tabs
    defaultValue="create"
    values={[
        { label: 'service_principals', value: 'create', },
        { label: 'Manifest', value: 'manifest', },
    ]}
>
<TabItem value="create">

```sql
/*+ create */
INSERT INTO databricks_workspace.iam.service_principals (
deployment_name,
data__schemas,
data__applicationId,
data__displayName,
data__groups,
data__roles,
data__entitlements,
data__externalId,
data__active
)
SELECT 
'{{ deployment_name }}',
'{{ schemas }}',
'{{ applicationId }}',
'{{ displayName }}',
'{{ groups }}',
'{{ roles }}',
'{{ entitlements }}',
'{{ externalId }}',
'{{ active }}'
;
```

</TabItem>
<TabItem value="manifest">

```yaml
- name: your_resource_model_name
  props:
  - name: schemas
    value:
    - urn:ietf:params:scim:schemas:core:2.0:ServicePrincipal
  - name: applicationId
    value: 97ab27fa-30e2-43e3-92a3-160e80f4c0d5
  - name: displayName
    value: etl-service
  - name: groups
    value:
    - $ref: string
      value: string
      display: string
      primary: true
      type: string
  - name: roles
    value:
    - $ref: string
      value: string
      display: string
      primary: true
      type: string
  - name: entitlements
    value:
    - $ref: string
      value: string
      display: string
      primary: true
      type: string
  - name: externalId
    value: string
  - name: active
    value: true

```

</TabItem>
</Tabs>

## `UPDATE` example

Updates a <code>service_principals</code> resource.

<Tabs
    defaultValue="patch"
    values={[
        { label: 'patch', value: 'patch' },
        { label: 'update', value: 'update' }
    ]
}>
<TabItem value="patch">

```sql
/*+ update */
-- replace field1, field2, etc. with the fields you want to update        
UPDATE databricks_workspace.iam.service_principals
SET field1 = '{{ value1 }}',
field2 = '{{ value2 }}', ...
WHERE id = '{{ id }}' AND
deployment_name = '{{ deployment_name }}';
```
</TabItem>
<TabItem value="update">

```sql
/*+ update */
-- replace field1, field2, etc. with the fields you want to update        
UPDATE databricks_workspace.iam.service_principals
SET field1 = '{{ value1 }}',
field2 = '{{ value2 }}', ...
WHERE id = '{{ id }}' AND
deployment_name = '{{ deployment_name }}';
```
</TabItem>
</Tabs>

## `DELETE` example

Deletes a <code>service_principals</code> resource.

```sql
/*+ delete */
DELETE FROM databricks_workspace.iam.service_principals
WHERE id = '{{ id }}' AND
deployment_name = '{{ deployment_name }}';
```