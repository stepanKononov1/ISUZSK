SELECT t.`task_id`, t.`name`, t.`executor`, t.`deadline`, ct.`column_id` FROM `Tasks` as t
JOIN `Columns_Tasks` as ct ON ct.`task_id` = t.`task_id`
JOIN `Columns` as c ON ct.`column_id` = c.`column_id`
WHERE c.`desk_id` = %s;