SELECT d.`desk_id`, d.`name` FROM `Projects` as p
JOIN `Companies_Projects` as cp ON cp.`project_id` = p.`project_id`
JOIN `Projects_Desks` as pd ON pd.`project_id` = p.`project_id`
JOIN `Desks` as d ON pd.`desk_id` = d.`desk_id`
WHERE cp.`company_id` = %s AND p.`project_id` = %s;