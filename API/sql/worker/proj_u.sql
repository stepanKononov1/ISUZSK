UPDATE `Projects`
SET 
`name` = %s,
`executor` = %s,
`start` = %s,
`deadline` = %s
WHERE `project_id` = %s;