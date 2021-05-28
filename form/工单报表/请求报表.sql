 select gr.workflow_id as '请求单号',
               gr.applicant as '处理人',
               gr.type as '服务请求类别',
               gr.created_at as '申请时间',
               pt1.assign_time as '响应时间',
               pt1.assign_time as '开始时间',
               gr.complete_at as '完成时间',
               IF(pt1.assign_time, TIMESTAMPDIFF(HOUR, gr.created_at,pt1.assign_time), '-') as '响应时长(小时)',
               IF(pt1.complete_at, TIMESTAMPDIFF(HOUR, gr.created_at,gr.complete_at), '-') as '完成时长(小时)',
               JSON_EXTRACT(pt2.form, '$.suggestion') as '服务评价',
               IF(grl1.incidentNumbers is not null,'是','否') as '是否转事件',
               grl1.incidentNumbers as '事件编号',
               IF(grl2.changeNumbers is not null,'是','否') as '是否转变更',
               grl2.changeNumbers as '变更编号',
               gr.description as '备注'
        from generic_request gr
                 left join (select a.request_id, a.form, a.assign_time, a.process_task_name, a.complete_at
                            from process_task as a
                                     left join (select max(created_at) as create_at, request_id, process_task_name
                                                from process_task
                                                group by request_id, process_task_name) as b
                                               on a.request_id = b.request_id
                                               //
                            where a.created_at = b.create_at) as pt1

                            //同一个处理时间查找最新的task-退回

                           on gr.id = pt1.request_id and pt1.process_task_name = '服务处理'
                           //按照流程查找数据

                 left join (select c.request_id, c.form, c.assign_time, c.process_task_name, c.complete_at
                            from process_task as c
                                     left join (select max(created_at) as create_at, request_id, process_task_name
                                                from process_task
                                                group by request_id, process_task_name) as d
                                               on c.request_id = d.request_id
                            where c.created_at = d.create_at) as pt2
                           on gr.id = pt2.request_id and pt2.process_task_name = '确认关闭'
                 left join (select f.source_id, group_concat(f.workflow_id,',') as  incidentNumbers
                             from (select t1.source_id, t2.workflow_id
                                   from generic_request_link t1
                                            left join generic_request t2
                                                      on t1.target_id = t2.id and t2.type = 'INCIDENT_SERVICE') as f
                             group by f.source_id) as grl1
                           on gr.id = grl1.source_id
                 left join (select f.source_id, group_concat(f.workflow_id,',') as  changeNumbers
                            from (select t1.source_id, t2.workflow_id
                                  from generic_request_link t1
                                           left join generic_request t2
                                                     on t1.target_id = t2.id and t2.type = 'CHANGE_SERVICE') as f
                            group by f.source_id) as grl2
                           on gr.id = grl2.source_id
 where type ='REQUEST_SERVICE';




SELECT
	gr.workflow_id AS '请求单号',
	gr.NAME AS '标题',
	gr.applicant AS '申请人',
	bg.NAME AS '申请人单位',
	pt1.assignee_name AS '响应人',
	pt1.assignee_name AS '处理人',
CASE
		gr.type 
		WHEN 'PROBLEM_SERVICE' THEN
		"问题工单" 
		WHEN 'CHANGE_SERVICE' THEN
		"变更工单" 
		WHEN 'REQUEST_SERVICE' THEN
		"请求工单" 
		WHEN 'INCIDENT_SERVICE' THEN
		"事件工单" 
	END '工单类型',
	gr.created_at AS '申请时间点',
	pt1.assign_time AS '响应时间点',
	pt1.assign_time AS '开始时间点',
	gr.complete_at AS '完成时间点',
IF
	( pt1.assign_time, TIMESTAMPDIFF( MINUTE, gr.created_at, pt1.assign_time ), '-' ) AS '响应时长(分钟)',
IF
	( pt1.complete_at, TIMESTAMPDIFF( MINUTE, gr.created_at, gr.complete_at ), '-' ) AS '完成时长(分钟)',
	JSON_EXTRACT( pt2.form, '$.suggestion' ) AS '服务评价',
IF
	( grl1.incidentNumbers IS NOT NULL, '是', '否' ) AS '是否转事件',
	grl1.incidentNumbers AS '事件编号',
IF
	( grl2.changeNumbers IS NOT NULL, '是', '否' ) AS '是否转变更',
	grl2.changeNumbers AS '变更编号',
	gr.description AS '备注' 
FROM
	generic_request gr
	LEFT JOIN (
	SELECT
		a.request_id,
		a.form,
		a.assign_time,
		a.process_task_name,
		a.complete_at,
		a.assignee_name 
	FROM
		process_task AS a
		LEFT JOIN ( SELECT max( created_at ) AS create_at, request_id, process_task_name FROM process_task GROUP BY request_id, process_task_name ) AS b ON a.request_id = b.request_id 
	WHERE
		a.created_at = b.create_at 
	) AS pt1 ON gr.id = pt1.request_id 
	AND pt1.process_task_name = '服务处理'
	LEFT JOIN (
	SELECT
		c.request_id,
		c.form,
		c.assign_time,
		c.process_task_name,
		c.assignee_name 
	FROM
		process_task AS c
		LEFT JOIN ( SELECT max( created_at ) AS create_at, request_id, process_task_name FROM process_task GROUP BY request_id, process_task_name ) AS d ON c.request_id = d.request_id 
	WHERE
		c.created_at = d.create_at 
	) AS pt2 ON gr.id = pt2.request_id 
	AND pt2.process_task_name = '确认关闭'
	LEFT JOIN (
	SELECT
		f.source_id,
		group_concat( f.workflow_id, ',' ) AS incidentNumbers 
	FROM
		(
		SELECT
			t1.source_id,
			t2.workflow_id 
		FROM
			generic_request_link t1
			LEFT JOIN generic_request t2 ON t1.target_id = t2.id 
			AND t2.type = 'INCIDENT_SERVICE' 
		) AS f 
	GROUP BY
		f.source_id 
	) AS grl1 ON gr.id = grl1.source_id
	LEFT JOIN (
	SELECT
		f.source_id,
		group_concat( f.workflow_id, ',' ) AS changeNumbers 
	FROM
		(
		SELECT
			t1.source_id,
			t2.workflow_id 
		FROM
			generic_request_link t1
			LEFT JOIN generic_request t2 ON t1.target_id = t2.id 
			AND t2.type = 'CHANGE_SERVICE' 
		) AS f 
	GROUP BY
		f.source_id 
	) AS grl2 ON gr.id = grl2.source_id
	LEFT JOIN business_group bg ON bg.id = gr.business_group_id 
WHERE 
	gr.workflow_id LIKE 'SR%'
	AND gr.applicant NOT LIKE 'System administrator';