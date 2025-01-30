SELECT COUNT(*) AS unfin FROM Tasks t JOIN Companies_Tasks ct ON t.task_id = ct.task_id WHERE t.executed = '0000-00-00 00:00:00' AND ct.company_id = %s AND t.start >= %s AND t.executed <= %s;
