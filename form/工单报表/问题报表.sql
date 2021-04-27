 select gr.workflow_id as '问题单号',
               gr.applicant as '处理人',
               JSON_EXTRACT(gr.form,'$.trouble_source'),
               gr.type as '服务请求类别',
               gr.created_at as '申请时间',
               pt1.assign_time as '调研开始时间',
               gr.complete_at as '完成时间',
               IF(pt1.assign_time, TIMESTAMPDIFF(HOUR, gr.created_at,pt1.assign_time), '-') as '响应时长(小时)',
               IF(pt1.complete_at, TIMESTAMPDIFF(HOUR, gr.created_at,gr.complete_at), '-') as '完成时长(小时)',
               JSON_EXTRACT(gr.form, '$.trouble_source') as '问题来源',
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
                 
                 
 where type ='PROBLEM_SERVICE';
