UPDATE `Tasks`
SET `executed` = NOW()
WHERE `task_id` = %s;
