SELECT * FROM `Projects` as p
JOIN `Companies_Projects` as cp ON cp.`project_id` = p.`project_id`
WHERE cp.`company_id` = %s AND p.`project_id` = %s;