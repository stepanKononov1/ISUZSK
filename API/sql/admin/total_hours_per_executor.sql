SELECT ui.`fullname`, CAST(SUM(TIMESTAMPDIFF(HOUR, t.start, t.executed)) AS DOUBLE) AS total_hours FROM Tasks t JOIN Companies_Tasks ct ON t.task_id = ct.task_id
JOIN `Users_info` as ui on ui.`user_id` = t.`executor`
WHERE t.executed != '0000-00-00 00:00:00' AND ct.company_id = %s AND t.start >= %s AND t.executed <= %s GROUP BY t.executor;
