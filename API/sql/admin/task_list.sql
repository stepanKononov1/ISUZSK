SELECT t.`task_id`, t.`name`, t.`deadline`, t.`priority`, t.`storypoints`, 1, 1, ui.`fullname`, 1, 1, 1, 1 FROM `Tasks` as t
JOIN `Users_info` as ui on ui.`user_id` = t.`executor`
JOIN `Companies_Tasks` as ct on ct.`task_id` = t.`task_id`
WHERE ct.`company_id` = %s;