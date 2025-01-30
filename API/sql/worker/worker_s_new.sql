SELECT u.`user_id`, ui.`fullname`, u.`uuid`, ui.`experience`, ui.`add`, ui.`contacts`, ui.`age` FROM `Users` as u
JOIN `Users_info` as ui ON ui.`user_id` = u.`user_id`
JOIN `Companies_Users` as cu ON cu.`user_id` = `u`.`user_id`
WHERE cu.`company_id` = %s and u.`user_id` = %s;