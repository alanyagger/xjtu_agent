### 爬虫代码 ```get_data.py```

#### 支持功能
个人课表查询、全校课表查询、课程查询、成绩查询、空闲教室查询



#### how to run:
Please **download** driver first: 
[Chrome Driver](https://developer.chrome.com/docs/chromedriver)


```bash
python get_data.py --username your_uid --password your_pwd --func the_func_you_want --term 2024-2025-2 (--other_arg)
```

Demo for all support function:
```bash
python get_data.py --username 2226124051 --password i_love_coding --func 空闲教室 --campus 兴庆校区 --buildings 东2 --room_type 普通教室 --date 2025-07-16 --start 1 --end 6

python get_data.py --username 2226124051 --password i_love_coding --func 课程查询

python get_data.py --username 2226124051 --password i_love_coding --func 成绩查询

python get_data.py --username 2226124051 --password i_love_coding --func 个人课表 --term 2024-2025-2

python get_data.py --username 2226124051 --password i_love_coding --func 全校课程 --term 2024-2025-3
```

The result of the run is shown in ```function_data.json```.