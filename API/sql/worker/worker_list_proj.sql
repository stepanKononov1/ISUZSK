SELECT u.`user_id`, u.`uuid`, ui.`fullname`  FROM `Users` as u
JOIN `Users_info` as ui ON ui.`user_id` = u.`user_id`
JOIN `Companies_Users` as cu ON cu.`user_id` = `u`.`user_id`
JOIN `Projects_Execution` as pe ON pe.`user_id` = u.`user_id`
WHERE cu.`company_id` = %s AND pe.`project_id` = %s;