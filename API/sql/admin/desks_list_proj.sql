SELECT d.`desk_id`, d.`name` FROM `Desks` as d
JOIN `Companies_Desks` as cd ON cd.`desk_id` = d.`desk_id` 
LEFT JOIN `Projects_Desks` as pd ON pd.`desk_id` = d.`desk_id`
WHERE cd.`company_id` = %s AND pd.`project_id` = %s;