SELECT ui.`fullname`, CAST(AVG(TIMESTAMPDIFF(HOUR, t.start, t.executed)) as DOUBLE) AS avg_exec_time FROM Tasks t
JOIN `Users_info` as ui on ui.`user_id` = t.`executor`
JOIN Companies_Tasks ct ON t.task_id = ct.task_id
WHERE t.executed != '0000-00-00 00:00:00' AND ct.company_id = %s AND t.start >= %s AND t.executed <= %s GROUP BY t.executor;
