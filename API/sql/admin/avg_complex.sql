SELECT CAST(AVG(t.storypoints) AS DOUBLE) AS avg_complex FROM Tasks t JOIN Companies_Tasks ct ON t.task_id = ct.task_id WHERE ct.company_id = %s AND t.start >= %s AND t.executed <= %s;
