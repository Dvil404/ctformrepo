 select gr.workflow_id as '事件单号',
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
                            where a.created_at = b.create_at) as pt1
                           on gr.id = pt1.request_id and pt1.process_task_name = '服务处理'
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
 where type ='INCIDENT_SERVICE';