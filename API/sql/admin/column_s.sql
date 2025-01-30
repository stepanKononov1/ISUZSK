SELECT c.`column_id`, c.`name`, c.`type`, d.`desk_id`, d.`name` FROM `Columns` as c
JOIN `Desks` as d ON d.`desk_id` = c.`desk_id`;
