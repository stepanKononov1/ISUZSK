SELECT t.`task_id`, t.`name`, t.`deadline`, t.`priority`, t.`storypoints`, t.`executor`, c.`column_id` FROM `Tasks` as t
JOIN `Columns_Tasks` as c ON c.`task_id` = t.`task_id`
WHERE t.`task_id` = %s;