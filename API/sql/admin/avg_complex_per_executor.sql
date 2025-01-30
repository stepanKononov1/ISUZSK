SELECT ui.`fullname`, CAST(AVG(t.storypoints) as DOUBLE) AS avg_complex FROM Tasks t
JOIN `Users_info` as ui on ui.`user_id` = t.`executor`
JOIN Companies_Tasks ct ON t.task_id = ct.task_id WHERE ct.company_id = %s AND t.start >= %s AND t.executed <= %s GROUP BY t.executor;
