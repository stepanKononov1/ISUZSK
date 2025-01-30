SELECT * FROM `Tasks` as t
JOIN `Companies_Tasks` as ct on ct.`task_id` = t.`task_id`
WHERE ct.`company_id` = %s;