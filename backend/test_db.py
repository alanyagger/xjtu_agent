def schedule_to_dict(schedule: DBSchedule) -> dict:
    """将数据库日程对象转换为前端需要的字典格式"""
    return {
        "id": schedule.id,
        "name": schedule.name,
        "start_time": schedule.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "end_time": schedule.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "color": schedule.color,
        "remark": schedule.remark,
        "schedule_calendar": {
            "color": schedule.color,
            "name": "默认日历"
        }
    }

def get_schedules(
    start: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取当前用户的日程列表（支持日期范围筛选）"""
    query = db.query(DBSchedule).filter(DBSchedule.user_id == current_user.username)
    
    # 日期筛选
    if start and end:
        try:
            # 将输入的日期字符串转换为datetime对象，时间部分设为00:00:00
            start_date = datetime.strptime(start, "%Y-%m-%d")
            # 结束日期设为当天的23:59:59，覆盖一整天
            end_date = datetime.strptime(end, "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)
            
            # 查询条件：日程的结束时间晚于开始日期，且日程的开始时间早于结束日期
            query = query.filter(
                DBSchedule.end_time >= start_date,
                DBSchedule.start_time <= end_date
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")

    return [schedule_to_dict(s) for s in query.all()]