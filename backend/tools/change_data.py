import json

def calculate_gpa(data):
    """
    计算各学期加权平均分和总平均分
    
    参数:
        data: 包含成绩数据的字典
    返回:
        包含各学期平均分和总平均分的字典
    """
    # 提取成绩列表
    scores = data['datas']['xscjcx']['rows']
    
    # 按学期分组
    term_scores = {}
    for score in scores:
        term = score['学期']
        # 跳过成绩为0的课程（可能是未完成或无效成绩）
        if score['成绩'] == 0:
            continue
        if term not in term_scores:
            term_scores[term] = []
        term_scores[term].append(score)
    
    # 计算各学期加权平均分
    term_gpa = {}
    total_credits = 0.0  # 总学分
    total_weighted_score = 0.0  # 总加权分数
    
    for term, courses in term_scores.items():
        term_credits = 0.0
        term_weighted = 0.0
        
        for course in courses:
            credit = course['学分']
            score = course['成绩']
            # 跳过学分为0的课程（如某些体育活动）
            if credit <= 0:
                continue
            
            term_credits += credit
            term_weighted += credit * score
        
        # 计算学期加权平均分
        if term_credits > 0:
            term_average = term_weighted / term_credits
            term_gpa[term] = {
                'average': round(term_average, 2),
                'total_credits': round(term_credits, 1),
                'course_count': len(courses)
            }
            
            # 累加至总学分和总加权分数
            total_credits += term_credits
            total_weighted_score += term_weighted
    
    # 计算总加权平均分
    total_average = round(total_weighted_score / total_credits, 2) if total_credits > 0 else 0
    
    sorted_term_gpa = dict(sorted(term_gpa.items(), key=lambda x: x[0]))

    return {
        'term_gpa': sorted_term_gpa,
        'total_average': total_average,
        'total_credits': round(total_credits, 1)
    }

def main():
    # 提供的JSON数据
    with open("成绩查询_data.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
    # 计算GPA
    result = calculate_gpa(json_data)

    print(result)
    
    # 按学期顺序排序（默认按字符串排序，符合学年学期格式）
    sorted_terms = sorted(result['term_gpa'].items(), key=lambda x: x[0])
    
    # 输出结果
    print("=" * 50)
    print("各学期加权平均分：")
    print("-" * 50)
    print(f"{'学期':<15} {'平均分':<10} {'总学分':<10} {'课程数量'}")
    print("-" * 50)
    for term, info in sorted_terms:
        print(f"{term:<15} {info['average']:<10} {info['total_credits']:<10} {info['course_count']}")

if __name__ == "__main__":
    main()